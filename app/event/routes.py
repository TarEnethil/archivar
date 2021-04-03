from app import db
from app.calendar.models import Epoch, Moon
from app.calendar.helpers import gen_calendar_stats, gen_epoch_choices, gen_month_choices, gen_day_choices
from app.event import bp
from app.event.forms import SettingsForm, EventForm, CategoryForm
from app.event.helpers import update_timestamp, get_events, gen_event_category_choices, get_events_by_category
from app.event.models import EventSetting, Event, EventCategory
from app.helpers import page_title, stretch_color, deny_access, moderator_required
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required

no_perm_url = "calendar.index"


@bp.route("/view/<int:id>/<string:name>", methods=["GET"])
@bp.route("/view/<int:id>", methods=["GET"])
@login_required
def view(id, name=None):
    event = Event.query.filter_by(id=id).first_or_404()
    moons = Moon.query.all()

    if not event.is_viewable_by_user():
        return deny_access(no_perm_url)

    if event.is_visible is False:
        flash("This Event is only visible to you.", "warning")

    return render_template("event/view.html", event=event, moons=moons,
                           title=page_title("View Event '{}'".format(event.name)))


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
    title = "All Events for {}".format(e.name)

    return render_template("event/list.html", events=events, epoch_flag=True, heading=title,
                           title=page_title("View Events in Epoch '{}'".format(e.name)))


@bp.route("/list/epoch-<int:e_id>/<string:e_name>/year-<int:year>", methods=["GET"])
@login_required
def list_epoch_year(e_id, year, e_name=None):
    e = Epoch.query.filter_by(id=e_id).first_or_404()
    events = get_events(e_id, year)
    title = "All events for year {}, {}".format(year, e.name)

    return render_template("event/list.html", events=events, epoch_year_flag=True, heading=title,
                           title=page_title("View Events in Year {}, epoch '{}'".format(year, e.name)))


@bp.route("/list/category-<int:c_id>/<string:c_name>", methods=["GET"])
@login_required
def list_category(c_id, c_name=None):
    c = EventCategory.query.filter_by(id=c_id).first_or_404()
    events = get_events_by_category(c_id)
    title = "All Events in Category {}".format(c.name)

    return render_template("event/list.html", events=events, category_flag=True, heading=title,
                           title=page_title("View Events in Category '{}'".format(c.name)))


# TODO Fix C901
@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():  # noqa: C901
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
        form.is_visible.data = True

        if settings.default_epoch:
            form.epoch.data = settings.default_epoch

        if settings.default_year:
            form.year.data = settings.default_year

    if form.validate_on_submit():
        new_event = Event(name=form.name.data,
                          category_id=form.category.data,
                          description=form.description.data,
                          epoch_id=form.epoch.data,
                          year=form.year.data,
                          month_id=form.month.data,
                          day=form.day.data,
                          duration=form.duration.data)

        new_event.is_visible = form.is_visible.data

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
            except ValueError:
                pass

        # will do nothing if var is not an int or not in choices
        if year:
            try:
                form.year.data = int(year)
            except ValueError:
                pass

        # will do nothing if var is not an int or not in choices
        if category_id:
            try:
                form.category.data = int(category_id)
            except ValueError:
                pass

    calendar_helper = gen_calendar_stats()
    return render_template("event/create.html", form=form, calendar=calendar_helper, title=page_title("Add Event"))


@bp.route("/edit/<int:id>/<string:name>", methods=["GET", "POST"])
@login_required
def edit(id, name=None):
    event = Event.query.filter_by(id=id).first_or_404()

    if not event.is_editable_by_user():
        return deny_access(no_perm_url)

    form = EventForm()
    form.submit.label.text = "Save Event"
    form.category.choices = gen_event_category_choices()
    form.epoch.choices = gen_epoch_choices()
    form.month.choices = gen_month_choices()

    if request.method == "POST":
        form.day.choices = gen_day_choices(form.month.data)
    else:
        form.day.choices = gen_day_choices(event.month_id)

    if not event.is_hideable_by_user():
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

        if event.is_hideable_by_user():
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

        if event.is_hideable_by_user():
            form.is_visible.data = event.is_visible

    calendar_helper = gen_calendar_stats()
    return render_template("event/edit.html", form=form, calendar=calendar_helper,
                           title=page_title("Edit Event '{}'".format(event.name)))


@bp.route("/delete/<int:id>/<string:name>")
@login_required
def delete(id, name=None):
    event = Event.query.filter_by(id=id).first_or_404()

    if not event.is_deletable_by_user():
        return deny_access(no_perm_url)

    db.session.delete(event)
    db.session.commit()

    flash("Event was deleted", "success")
    return redirect(url_for("calendar.index"))


@bp.route("/category/create", methods=["GET", "POST"])
@login_required
@moderator_required(no_perm_url)
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
@moderator_required(no_perm_url)
def category_edit(id, name=None):
    form = CategoryForm()
    form.submit.label.text = "Edit Category"

    category = EventCategory.query.filter_by(id=id).first_or_404()
    heading = "Edit Event Category '{}'".format(category.name)

    if form.validate_on_submit():
        category.name = form.name.data
        category.color = stretch_color(form.color.data.hex)

        db.session.commit()

        flash("Event category edited.", "success")
        return redirect(url_for("event.settings"))
    elif request.method == "GET":
        form.name.data = category.name
        form.color.data = category.color

    return render_template("event/category.html", category=category, form=form, heading=heading,
                           title=page_title(heading))


@bp.route("/settings", methods=["GET", "POST"])
@login_required
@moderator_required(no_perm_url)
def settings():
    settings = EventSetting.query.get(1)
    form = SettingsForm()
    form.default_category.choices = gen_event_category_choices()
    form.default_epoch.choices = gen_epoch_choices()

    if form.validate_on_submit():
        settings.default_category = form.default_category.data
        settings.default_epoch = form.default_epoch.data
        settings.default_year = form.default_year.data

        db.session.commit()

        flash("Event settings have been changed.", "success")
    elif request.method == "GET":
        form.default_category.data = settings.default_category
        form.default_epoch.data = settings.default_epoch
        form.default_year.data = settings.default_year

    categories = EventCategory.query.all()

    return render_template("event/settings.html", settings=settings, categories=categories, form=form,
                           title=page_title("Event Settings"))


@bp.route("/sidebar", methods=["GET"])
@login_required
def sidebar():
    entries = Event.get_query_for_invisible_items(include_hidden_for_user=True)
    entries = entries.with_entities(Event.id, Event.name, Event.is_visible).order_by(Event.name.asc()).all()

    return jsonify(entries)
