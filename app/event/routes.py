from app import db
from app.helpers import page_title, redirect_non_admins, gen_calendar_stats, redirect_non_event_admins, gen_event_category_choices, gen_epoch_choices, gen_month_choices, gen_day_choices, update_timestamp
from app.models import EventSetting, Event, EventCategory
from app.event import bp
from app.event.forms import SettingsForm, EventForm, CategoryForm
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user

no_perm = "calendar.index"

@bp.route("/dummy", methods=["GET"])
@login_required
def dummy():
    return redirect(url_for("index"))

@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    settings = EventSetting.query.get(1)
    form = EventForm()
    form.category.choices = gen_event_category_choices()
    form.epoch.choices = gen_epoch_choices()
    form.month.choices = gen_month_choices()

    if request.method == "POST":
        form.day.choices = gen_day_choices(form.month.data)
    else:
        form.day.choices = gen_day_choices(1)
        form.category.data = settings.default_category
        form.is_visible.data = settings.default_visible


    if not current_user.is_event_admin():
        del form.is_visible

    if form.validate_on_submit():
        new_event = Event(name=form.name.data, category_id=form.category.data, description=form.description.data, epoch_id=form.epoch.data, year=form.year.data, month_id=form.month.data, day=form.day.data, duration=form.duration.data, created_by_id=current_user.id)

        if current_user.is_event_admin():
            new_event.is_visible = form.is_visible.data
        else:
            new_event.is_visible = settings.default_visible

        db.session.add(new_event)
        db.session.commit()

        update_timestamp(new_event.id)

        flash("Event was created.", "success")
        return redirect(url_for("calendar.index"))

    calendar_helper = gen_calendar_stats()
    return render_template("event/create.html", form=form, calendar=calendar_helper, title=page_title("Create new event"))

@bp.route("/category/create", methods=["GET", "POST"])
@login_required
def category_create():
    deny_access = redirect_non_event_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    heading = "Create new event category"
    form = CategoryForm()

    if form.validate_on_submit():
        new_category = EventCategory(name=form.name.data, color=form.color.data.hex)

        db.session.add(new_category)
        db.session.commit()

        flash("Category created.", "success")
        return redirect(url_for("event.settings"))

    return render_template("event/category.html", form=form, heading=heading, title=page_title(heading))

@bp.route("/category/edit/<int:id>", methods=["GET", "POST"])
@login_required
def category_edit(id):
    deny_access = redirect_non_event_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    heading = "Edit event category"
    form = CategoryForm()

    category = EventCategory.query.filter_by(id=id).first_or_404()

    if form.validate_on_submit():
        category.name = form.name.data
        category.color = form.color.data.hex

        db.session.commit()

        flash("Event category edited.", "success")
        return redirect(url_for("event.settings"))
    elif request.method == "GET":
        form.name.data = category.name
        form.color.data = category.color

    return render_template("event/category.html", form=form, heading=heading, title=page_title(heading))

@bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    deny_access = redirect_non_event_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    settings = EventSetting.query.get(1)
    form = SettingsForm()
    form.default_category.choices = gen_event_category_choices()

    if form.validate_on_submit():
        settings.default_visible = form.default_visible.data
        settings.default_category = form.default_category.data

        db.session.commit()

        flash("Event settings have been changed.", "success")
    elif request.method == "GET":
        form.default_visible.data = settings.default_visible
        form.default_category.data = settings.default_category

    categories = EventCategory.query.all()

    return render_template("event/settings.html", categories=categories, form=form, title=page_title("Event settings"))