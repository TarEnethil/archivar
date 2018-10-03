from app import db
from app.helpers import page_title, redirect_non_admins, gen_calendar_stats, redirect_non_event_admins
from app.models import EventCategory
from app.event import bp
from app.event.forms import CategoryForm
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required

no_perm = "calendar.index"

@bp.route("/dummy", methods=["GET"])
@login_required
def dummy():
    return redirect(url_for("index"))

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

@bp.route("/settings", methods=["GET"])
@login_required
def settings():
    deny_access = redirect_non_event_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    categories = EventCategory.query.all()

    return render_template("event/settings.html", categories=categories, title=page_title("Event settings"))