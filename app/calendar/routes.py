from app import db
from app.helpers import page_title, redirect_non_admins, get_next_epoch_order
from app.models import CalendarSetting, Epoch
from app.calendar import bp
from app.calendar.forms import EpochForm
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required

no_perm = "index"

@bp.route("/settings", methods=["GET"])
@login_required
def settings():
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    cset = CalendarSetting.query.get(1)

    epochs = Epoch.query.order_by(Epoch.order.asc()).all()

    return render_template("calendar/settings.html", settings=cset, epochs=epochs, title=page_title("Calendar settings"))

@bp.route("/dummy", methods=["GET"])
@login_required
def dummy():
    return redirect(url_for("index"))

@bp.route("/epoch/create", methods=["GET", "POST"])
@login_required
def epoch_create():
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    heading = "Create new epoch"
    form = EpochForm()

    if form.validate_on_submit():
        order_num = get_next_epoch_order()

        new_epoch = Epoch(name=form.name.data, abbreviation=form.abbreviation.data, description=form.description.data, years=form.years.data, circa=form.circa.data, order=order_num)

        db.session.add(new_epoch)
        db.session.commit()

        flash("Epoch added.", "success")
        return redirect(url_for("calendar.settings"))

    return render_template("calendar/form.html", form=form, heading=heading, title=page_title("Create new epoch"))

@bp.route("/epoch/edit/<int:id>", methods=["GET", "POST"])
@login_required
def epoch_edit(id):
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    heading = "Edit epoch"
    form = EpochForm()

    epoch = Epoch.query.filter_by(id=id).first_or_404()

    if form.validate_on_submit():
        epoch.name = form.name.data
        epoch.abbreviation = form.abbreviation.data
        epoch.description = form.description.data
        epoch.years = form.years.data
        epoch.circa = form.circa.data

        db.session.commit()

        flash("Epoch edited.", "success")
        return redirect(url_for("calendar.settings"))
    elif request.method == "GET":
        form.name.data = epoch.name
        form.abbreviation.data = epoch.abbreviation
        form.description.data = epoch.description
        form.years.data = epoch.years
        form.circa.data = epoch.circa

    return render_template("calendar/form.html", form=form, heading=heading, title=page_title("Edit epoch"))

@bp.route("/epoch/delete/<int:id>", methods=["GET"])
@login_required
def epoch_delete(id):
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    epoch = Epoch.query.filter_by(id=id).first_or_404()

    db.session.delete(epoch)
    db.session.commit()

    flash("Epoch was deleted.", "success")
    return redirect(url_for("calendar.settings"))


@bp.route("/epoch/up/<int:id>", methods=["GET"])
@login_required
def epoch_up(id):
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    epoch_to_up = Epoch.query.filter_by(id=id).first_or_404()
    epoch_to_down = Epoch.query.filter(Epoch.order < epoch_to_up.order).order_by(Epoch.order.desc()).limit(1).first()

    if not epoch_to_down:
        flash("No epoch with lower order found.", "danger")
        return redirect(url_for("calendar.settings"))

    up_order = epoch_to_up.order
    down_order = epoch_to_down.order

    epoch_to_up.order = down_order
    epoch_to_down.order = up_order

    db.session.commit()

    flash("Order of '" + epoch_to_up.name + "' and '" + epoch_to_down.name + "' has been swapped.", "success")
    return redirect(url_for("calendar.settings"))

@bp.route("/epoch/down/<int:id>", methods=["GET"])
@login_required
def epoch_down(id):
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    epoch_to_down = Epoch.query.filter_by(id=id).first_or_404()
    epoch_to_up = Epoch.query.filter(Epoch.order > epoch_to_down.order).order_by(Epoch.order.asc()).limit(1).first()

    if not epoch_to_up:
        flash("No epoch with higher order found.", "danger")
        return redirect(url_for("calendar.settings"))

    down_order = epoch_to_down.order
    up_order = epoch_to_up.order

    epoch_to_down.order = up_order
    epoch_to_up.order = down_order

    db.session.commit()

    flash("Order of '" + epoch_to_down.name + "' and '" + epoch_to_up.name + "' has been swapped.", "success")
    return redirect(url_for("calendar.settings"))