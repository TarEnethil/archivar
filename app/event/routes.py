from app import db
from app.calendar.models import Epoch, Moon
from app.calendar.helpers import gen_calendar_stats, gen_epoch_choices, gen_month_choices, gen_day_choices
from app.event import bp
from app.event.forms import SettingsForm, EventForm, CategoryForm
from app.event.helpers import event_admin_required, update_timestamp, get_events, gen_event_category_choices, get_events_by_category
from app.event.models import EventSetting, Event, EventCategory
from app.helpers import page_title, flash_no_permission, stretch_color
from app.user.models import User, Role
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import not_, and_, or_

no_perm_url = "calendar.index"

@bp.route("/view/<int:id>/<string:name>", methods=["GET"])
@bp.route("/view/<int:id>", methods=["GET"])
@login_required
def view(id, name=None):
    event = Event.query.filter_by(id=id).first_or_404()
    moons = Moon.query.all()

    # TODO: write decorator for this?
    if not current_user.is_event_admin() and event.is_visible == False and not event.created_by == current_user:
        flash_no_permission()
        return redirect(url_for(no_perm_url))

    if not current_user.has_admin_role() and current_user.has_event_role() and event.is_visible == False and event.created_by.has_admin_role():
        flash_no_permission()
        return redirect(url_for(no_perm_url))

    return render_template("event/view.html", event=event, moons=moons, title=page_title("View Event '%s'" % event.name))

@bp.route("/list", methods=["GET"])
@login_required
def list():
    title = "All Events"
    events = get_events()

    return render_template("event/list.html", events=events, heading=title, title=page_title("View All Events"))

@bp.route("/list/epoch-<int:e_id>/<string:e_name>", methods=["GET"])
@login_required
def list_epoch(e_id, e_name=None):
    e = Epoch.query.filter_by(id=e_id).first_or_404()
    events = get_events(e_id)
    title = "All Events for " + e.name

    return render_template("event/list.html", events=events, epoch_flag=True, heading=title, title=page_title("View Events in Epoch '%s'" % e.name))

@bp.route("/list/epoch-<int:e_id>/<string:e_name>/year-<int:year>", methods=["GET"])
@login_required
def list_epoch_year(e_id, year, e_name=None):
    e = Epoch.query.filter_by(id=e_id).first_or_404()
    events = get_events(e_id, year)
    title = "All events for year " + str(year) + ", " + e.name

    return render_template("event/list.html", events=events, epoch_year_flag=True, heading=title, title=page_title("View Events in Year %s, epoch '%s'" % (year, e.name)))

@bp.route("/list/category-<int:c_id>/<string:c_name>", methods=["GET"])
@login_required
def list_category(c_id, c_name=None):
    c = EventCategory.query.filter_by(id=c_id).first_or_404()
    events = get_events_by_category(c_id)
    title = "All Events in Category " + c.name

    return render_template("event/list.html", events=events, category_flag=True, heading=title, title=page_title("View Events in Category '%s'" % c.name))

@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    settings = EventSetting.query.get(1)
    form = EventForm()
    form.submit.label.text = "Create Event"
    form.category.choices = gen_event_category_choices()
    form.epoch.choices = gen_epoch_choices()
    form.month.choices = gen_month_choices()

    if request.method == "POST":
        form.day.choices = gen_day_choices(form.month.data)
    else:
        form.day.choices = gen_day_choices(1)
        form.category.data = settings.default_category
        form.is_visible.data = settings.default_visible

        if settings.default_epoch:
            form.epoch.data = settings.default_epoch

        if settings.default_year:
            form.year.data = settings.default_year

    if not current_user.is_event_admin():
        del form.is_visible

    if form.validate_on_submit():
        new_event = Event(name=form.name.data, category_id=form.category.data, description=form.description.data, epoch_id=form.epoch.data, year=form.year.data, month_id=form.month.data, day=form.day.data, duration=form.duration.data)

        if current_user.is_event_admin():
            new_event.is_visible = form.is_visible.data
        else:
            new_event.is_visible = settings.default_visible

        db.session.add(new_event)
        db.session.commit()

        update_timestamp(new_event.id)

        flash("Event was created.", "success")
        return redirect(new_event.view_url())
    elif request.method == "GET":
        # pre-select fields if get-params were passed
        epoch_id = request.args.get("epoch")
        year = request.args.get("year")
        category_id = request.args.get("category")

        # will do nothing if var is not an int or not in choices
        if epoch_id:
            try:
                form.epoch.data = int(epoch_id)
            except:
                pass

        # will do nothing if var is not an int or not in choices
        if year:
            try:
                form.year.data = int(year)
            except:
                pass

        # will do nothing if var is not an int or not in choices
        if category_id:
            try:
                form.category.data = int(category_id)
            except:
                pass

    calendar_helper = gen_calendar_stats()
    return render_template("event/create.html", form=form, calendar=calendar_helper, title=page_title("Add Event"))

@bp.route("/edit/<int:id>/<string:name>", methods=["GET", "POST"])
@login_required
def edit(id, name=None):
    event = Event.query.filter_by(id=id).first_or_404()

    form = EventForm()
    form.submit.label.text = "Save Event"
    form.category.choices = gen_event_category_choices()
    form.epoch.choices = gen_epoch_choices()
    form.month.choices = gen_month_choices()

    if request.method == "POST":
        form.day.choices = gen_day_choices(form.month.data)
    else:
        form.day.choices = gen_day_choices(event.month_id)

    # TODO: write custom decorator for this?
    if not current_user.has_admin_role() and current_user.has_event_role() and event.is_visible == False and event.created_by.has_admin_role():
        flash_no_permission()
        return redirect(url_for(no_perm_url))

    if not current_user.is_event_admin() and event.is_visible == False and not event.created_by == current_user:
        flash_no_permission()
        return redirect(url_for(no_perm_url))

    if not current_user.is_event_admin():
        del form.is_visible

    if form.validate_on_submit():
        event.name = form.name.data
        event.category_id = form.category.data
        event.description = form.description.data
        event.epoch_id = form.epoch.data
        event.year = form.year.data
        event.month_id = form.month.data
        event.day = form.day.data
        event.duration = form.duration.data

        if current_user.is_event_admin():
            event.is_visible = form.is_visible.data

        db.session.commit()

        update_timestamp(event.id)

        flash("Event was edited.", "success")

        return redirect(event.view_url())
    elif request.method == "GET":
        form.name.data = event.name
        form.category.data = event.category_id
        form.description.data = event.description
        form.epoch.data = event.epoch_id
        form.year.data = event.year
        form.month.data = event.month_id
        form.day.data = event.day
        form.duration.data = event.duration

        if current_user.is_event_admin():
            form.is_visible.data = event.is_visible

    calendar_helper = gen_calendar_stats()
    return render_template("event/edit.html", form=form, calendar=calendar_helper, title=page_title("Edit Event '%s'" % event.name))

@bp.route("/delete/<int:id>/<string:name>")
@login_required
def delete(id, name=None):
    event = Event.query.filter_by(id=id).first_or_404()

    # TODO: write custom decorator for this?
    if not current_user.has_admin_role() and current_user.has_event_role() and event.is_visible == False and event.created_by.has_admin_role():
        flash_no_permission()
        return redirect(url_for(no_perm_url))

    if not current_user.is_event_admin() and event.is_visible == False and not event.created_by == current_user:
        flash_no_permission()
        return redirect(url_for(no_perm_url))

    db.session.delete(event)
    db.session.commit()

    flash("Event was deleted", "success")
    return redirect(url_for("calendar.index"))

@bp.route("/category/create", methods=["GET", "POST"])
@login_required
@event_admin_required
def category_create():
    heading = "Add Event Category"
    form = CategoryForm()
    form.submit.label.text = "Create Category"

    if form.validate_on_submit():
        new_category = EventCategory(name=form.name.data, color=stretch_color(form.color.data.hex))

        db.session.add(new_category)
        db.session.commit()

        flash("Category created.", "success")
        return redirect(url_for("event.settings"))

    return render_template("event/category.html", form=form, heading=heading, title=page_title(heading))

@bp.route("/category/edit/<int:id>/<string:name>", methods=["GET", "POST"])
@login_required
@event_admin_required
def category_edit(id, name=None):
    form = CategoryForm()
    form.submit.label.text = "Edit Category"

    category = EventCategory.query.filter_by(id=id).first_or_404()
    heading = "Edit Event Category '%s'" % category.name

    if form.validate_on_submit():
        category.name = form.name.data
        category.color = stretch_color(form.color.data.hex)

        db.session.commit()

        flash("Event category edited.", "success")
        return redirect(url_for("event.settings"))
    elif request.method == "GET":
        form.name.data = category.name
        form.color.data = category.color

    return render_template("event/category.html", category=category, form=form, heading=heading, title=page_title(heading))

@bp.route("/settings", methods=["GET", "POST"])
@login_required
@event_admin_required
def settings():
    settings = EventSetting.query.get(1)
    form = SettingsForm()
    form.default_category.choices = gen_event_category_choices()
    form.default_epoch.choices = gen_epoch_choices()

    if form.validate_on_submit():
        settings.default_visible = form.default_visible.data
        settings.default_category = form.default_category.data
        settings.default_epoch = form.default_epoch.data
        settings.default_year = form.default_year.data

        db.session.commit()

        flash("Event settings have been changed.", "success")
    elif request.method == "GET":
        form.default_visible.data = settings.default_visible
        form.default_category.data = settings.default_category
        form.default_epoch.data = settings.default_epoch
        form.default_year.data = settings.default_year

    categories = EventCategory.query.all()

    return render_template("event/settings.html", settings=settings, categories=categories, form=form, title=page_title("Event Settings"))

@bp.route("/sidebar", methods=["GET"])
@login_required
def sidebar():
    if current_user.has_admin_role():
        entries = Event.query
    elif current_user.has_event_role():
        admins = User.query.filter(User.roles.contains(Role.query.get(1)))
        admin_ids = [a.id for a in admins]
        entries = Event.query.filter(not_(and_(Event.is_visible == False, Event.created_by_id.in_(admin_ids))))
    else:
        entries = Event.query.filter(or_(Event.is_visible == True, Event.created_by_id == current_user.id))

    entries = entries.with_entities(Event.id, Event.name, Event.is_visible).order_by(Event.name.asc()).all()

    return jsonify(entries)