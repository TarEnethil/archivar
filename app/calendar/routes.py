from app import db
from app.helpers import page_title, redirect_non_admins, get_next_epoch_order, get_next_month_order, get_next_day_order
from app.models import CalendarSetting, Epoch, Month, Day
from app.calendar import bp
from app.calendar.forms import EpochForm, MonthForm
from flask import render_template, flash, redirect, url_for, request
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
    months = Month.query.order_by(Month.order.asc()).all()
    days = Day.query.order_by(Day.order.asc()).all()

    return render_template("calendar/settings.html", settings=cset, epochs=epochs, months=months, days=days, title=page_title("Calendar settings"))

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

@bp.route("/month/create", methods=["GET", "POST"])
@login_required
def month_create():
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    heading = "Create new month"
    form = MonthForm()

    if form.validate_on_submit():
        order_num = get_next_month_order()

        new_month = Month(name=form.name.data, abbreviation=form.abbreviation.data, description=form.description.data, days=form.days.data, order=order_num)

        db.session.add(new_month)
        db.session.commit()

        flash("Month added.", "success")
        return redirect(url_for("calendar.settings"))

    return render_template("calendar/form.html", form=form, heading=heading, title=page_title("Create new month"))

@bp.route("/month/edit/<int:id>", methods=["GET", "POST"])
@login_required
def month_edit(id):
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    heading = "Edit month"
    form = MonthForm()

    month = Month.query.filter_by(id=id).first_or_404()

    if form.validate_on_submit():
        month.name = form.name.data
        month.abbreviation = form.abbreviation.data
        month.description = form.description.data
        month.days = form.days.data

        db.session.commit()

        flash("Month edited.", "success")
        return redirect(url_for("calendar.settings"))
    elif request.method == "GET":
        form.name.data = month.name
        form.abbreviation.data = month.abbreviation
        form.description.data = month.description
        form.days.data = month.days

    return render_template("calendar/form.html", form=form, heading=heading, title=page_title("Edit month"))

@bp.route("/month/delete/<int:id>", methods=["GET"])
@login_required
def month_delete(id):
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    month = Month.query.filter_by(id=id).first_or_404()

    db.session.delete(month)
    db.session.commit()

    flash("Month was deleted.", "success")
    return redirect(url_for("calendar.settings"))


@bp.route("/month/up/<int:id>", methods=["GET"])
@login_required
def month_up(id):
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    month_to_up = Month.query.filter_by(id=id).first_or_404()
    month_to_down = Month.query.filter(Month.order < month_to_up.order).order_by(Month.order.desc()).limit(1).first()

    if not month_to_down:
        flash("No month with lower order found.", "danger")
        return redirect(url_for("calendar.settings"))

    up_order = month_to_up.order
    down_order = month_to_down.order

    month_to_up.order = down_order
    month_to_down.order = up_order

    db.session.commit()

    flash("Order of '" + month_to_up.name + "' and '" + month_to_down.name + "' has been swapped.", "success")
    return redirect(url_for("calendar.settings"))

@bp.route("/month/down/<int:id>", methods=["GET"])
@login_required
def month_down(id):
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    month_to_down = Month.query.filter_by(id=id).first_or_404()
    month_to_up = Month.query.filter(Month.order > month_to_down.order).order_by(Month.order.asc()).limit(1).first()

    if not month_to_up:
        flash("No month with higher order found.", "danger")
        return redirect(url_for("calendar.settings"))

    down_order = month_to_down.order
    up_order = month_to_up.order

    month_to_down.order = up_order
    month_to_up.order = down_order

    db.session.commit()

    flash("Order of '" + month_to_down.name + "' and '" + month_to_up.name + "' has been swapped.", "success")
    return redirect(url_for("calendar.settings"))