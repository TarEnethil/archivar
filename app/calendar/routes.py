from app import db
from app.helpers import page_title, admin_required, stretch_color
from app.models import CalendarSetting, Epoch, Month, Day, Moon
from app.calendar import bp
from app.calendar.forms import EpochForm, MonthForm, DayForm, MoonForm
from app.calendar.helpers import get_next_epoch_order, get_next_month_order, get_next_day_order, calendar_sanity_check, gen_calendar_preview_data, gen_calendar_stats, get_years_in_epoch, get_epochs, gen_epoch_choices, gen_month_choices, gen_day_choices
from app.event.forms import EventForm
from app.event.helpers import get_event_categories
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user

no_perm_url = "index"

@bp.route("/settings", methods=["GET"])
@login_required
@admin_required(no_perm_url)
def settings():
    cset = CalendarSetting.query.get(1)

    epochs = Epoch.query.order_by(Epoch.order.asc()).all()
    months = Month.query.order_by(Month.order.asc()).all()
    days = Day.query.order_by(Day.order.asc()).all()
    moons = Moon.query.order_by(Moon.name.asc()).all()

    return render_template("calendar/settings.html", settings=cset, epochs=epochs, months=months, days=days, moons=moons, title=page_title("Calendar Settings"))

@bp.route("/", methods=["GET"])
@login_required
def index():
    cset = CalendarSetting.query.get(1)
    calendar = None

    if cset.finalized == True:
        calendar = gen_calendar_stats()
    elif current_user.has_admin_role():
        flash("The calendar has not been finalized, you have been redirected to the calendar setup.", "warning")
        return redirect(url_for('calendar.settings'))

    epochs = get_epochs()
    years = {}

    for e in epochs:
        years[e.id] = get_years_in_epoch(e.id)

    categories = get_event_categories()

    return render_template("calendar/index.html", settings=cset, calendar=calendar, epochs=epochs, years=years, categories=categories, title=page_title("Calendar"))

@bp.route("/view", methods=["GET"])
@login_required
def view():
    cset = CalendarSetting.query.get(1)
    stats = None

    if cset.finalized == True:
        stats = gen_calendar_stats()

    return render_template("calendar/view.html", settings=cset, stats=stats, title=page_title("View calendar"))

@bp.route("/check", methods=["GET"])
@login_required
@admin_required(no_perm_url)
def check():
    cset = CalendarSetting.query.get(1)
    if cset.finalized == True:
            flash("Calendar has already been finalized, check not possible.", "danger")
            return redirect(url_for('calendar.index'))

    status = calendar_sanity_check()

    if status == True:
        flash("All checks have passed. The calendar works with this configuration.", "success")
    else:
        flash("There were errors checking the calendar. See the other messages for more details.", "danger")

    return redirect(url_for("calendar.settings"))

@bp.route("/preview", methods=["GET"])
@login_required
@admin_required(no_perm_url)
def preview():
    cset = CalendarSetting.query.get(1)
    if cset.finalized == True:
        flash("Calendar has already been finalized, preview not possible.", "danger")
        return redirect(url_for('calendar.index'))

    status = calendar_sanity_check()

    if status == False:
        flash("There were errors previewing the calendar. See the other messages for more details.", "danger")
        return redirect(url_for("calendar.settings"))
    else:
        flash("All checks passed.", "success")

    stats = gen_calendar_preview_data()

    preview_form = EventForm()

    del preview_form.submit
    del preview_form.name
    del preview_form.category
    del preview_form.is_visible
    del preview_form.description

    preview_form.epoch.choices = gen_epoch_choices()
    preview_form.month.choices = gen_month_choices()
    preview_form.day.choices = gen_day_choices(1)

    return render_template("calendar/preview.html", calendar=stats, form=preview_form, title=page_title("Preview calendar"))

@bp.route("/finalize", methods=["GET"])
@login_required
@admin_required(no_perm_url)
def finalize():
    cset = CalendarSetting.query.get(1)
    if cset.finalized == True:
            flash("Calendar has already been finalized.", "danger")
            return redirect(url_for('calendar.index'))

    status = calendar_sanity_check()

    if status == False:
        flash("There were errors finalizing the calendar. See the other messages for more details.", "danger")
        return redirect(url_for("calendar.settings"))

    gen_calendar_preview_data(commit=True)
    cset = CalendarSetting.query.get(1)
    cset.finalized = True
    db.session.commit()

    flash("The calendar was finalized.", "success")
    return redirect(url_for('calendar.settings'))

@bp.route("/epoch/create", methods=["GET", "POST"])
@login_required
@admin_required(no_perm_url)
def epoch_create():
    cset = CalendarSetting.query.get(1)
    if cset.finalized == True:
        flash("The calendar is finalized. You can't add new epochs.", "danger")
        return redirect(url_for('calendar.settings'))

    heading = "Create New Epoch"
    form = EpochForm()
    form.submit.label.text = "Create Epoch"

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
@admin_required(no_perm_url)
def epoch_edit(id):
    heading = "Edit Epoch"
    form = EpochForm()
    form.submit.label.text = "Save Epoch"

    cset = CalendarSetting.query.get(1)
    if cset.finalized == True:
        del form.years
        del form.circa

    epoch = Epoch.query.filter_by(id=id).first_or_404()

    if form.validate_on_submit():
        epoch.name = form.name.data
        epoch.abbreviation = form.abbreviation.data
        epoch.description = form.description.data

        if cset.finalized == False:
            epoch.years = form.years.data
            epoch.circa = form.circa.data

        db.session.commit()

        flash("Epoch edited.", "success")
        return redirect(url_for("calendar.settings"))
    elif request.method == "GET":
        form.name.data = epoch.name
        form.abbreviation.data = epoch.abbreviation
        form.description.data = epoch.description

        if cset.finalized == False:
            form.years.data = epoch.years
            form.circa.data = epoch.circa

    return render_template("calendar/form.html", item=epoch, form=form, heading=heading, title=page_title("Edit epoch '%s'" % epoch.name))

@bp.route("/epoch/delete/<int:id>", methods=["GET"])
@login_required
@admin_required(no_perm_url)
def epoch_delete(id):
    cset = CalendarSetting.query.get(1)
    if cset.finalized == True:
        flash("The calendar is finalized. You can't delete epochs.", "danger")
        return redirect(url_for('calendar.settings'))

    epoch = Epoch.query.filter_by(id=id).first_or_404()

    db.session.delete(epoch)
    db.session.commit()

    flash("Epoch was deleted.", "success")
    return redirect(url_for("calendar.settings"))


@bp.route("/epoch/up/<int:id>", methods=["GET"])
@login_required
@admin_required(no_perm_url)
def epoch_up(id):
    cset = CalendarSetting.query.get(1)
    if cset.finalized == True:
        flash("The calendar is finalized. You can't change the order of epochs.", "danger")
        return redirect(url_for('calendar.settings'))

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
@admin_required(no_perm_url)
def epoch_down(id):
    cset = CalendarSetting.query.get(1)
    if cset.finalized == True:
        flash("The calendar is finalized. You can't change the order of epochs.", "danger")
        return redirect(url_for('calendar.settings'))

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
@admin_required(no_perm_url)
def month_create():
    cset = CalendarSetting.query.get(1)
    if cset.finalized == True:
        flash("The calendar is finalized. You can't add new months.", "danger")
        return redirect(url_for('calendar.settings'))

    heading = "Create New Month"
    form = MonthForm()
    form.submit.label.text = "Create Month"

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
@admin_required(no_perm_url)
def month_edit(id):
    heading = "Edit Month"
    form = MonthForm()
    form.submit.label.text = "Save Month"

    cset = CalendarSetting.query.get(1)
    if cset.finalized == True:
        del form.days

    month = Month.query.filter_by(id=id).first_or_404()

    if form.validate_on_submit():
        month.name = form.name.data
        month.abbreviation = form.abbreviation.data
        month.description = form.description.data

        if cset.finalized == False:
            month.days = form.days.data

        db.session.commit()

        flash("Month edited.", "success")
        return redirect(url_for("calendar.settings"))
    elif request.method == "GET":
        form.name.data = month.name
        form.abbreviation.data = month.abbreviation
        form.description.data = month.description

        if cset.finalized == False:
            form.days.data = month.days

    return render_template("calendar/form.html", item=month, form=form, heading=heading, title=page_title("Edit month '%s'" % month.name))

@bp.route("/month/delete/<int:id>", methods=["GET"])
@login_required
@admin_required(no_perm_url)
def month_delete(id):
    cset = CalendarSetting.query.get(1)
    if cset.finalized == True:
        flash("The calendar is finalized. You can't deletet months.", "danger")
        return redirect(url_for('calendar.settings'))

    month = Month.query.filter_by(id=id).first_or_404()

    db.session.delete(month)
    db.session.commit()

    flash("Month was deleted.", "success")
    return redirect(url_for("calendar.settings"))


@bp.route("/month/up/<int:id>", methods=["GET"])
@login_required
@admin_required(no_perm_url)
def month_up(id):
    cset = CalendarSetting.query.get(1)
    if cset.finalized == True:
        flash("The calendar is finalized. You can't change the order of months.", "danger")
        return redirect(url_for('calendar.settings'))

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
@admin_required(no_perm_url)
def month_down(id):
    cset = CalendarSetting.query.get(1)
    if cset.finalized == True:
        flash("The calendar is finalized. You can't change the order of months.", "danger")
        return redirect(url_for('calendar.settings'))

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

@bp.route("/day/create", methods=["GET", "POST"])
@login_required
@admin_required(no_perm_url)
def day_create():
    cset = CalendarSetting.query.get(1)
    if cset.finalized == True:
        flash("The calendar is finalized. You can't add new days.", "danger")
        return redirect(url_for('calendar.settings'))

    heading = "Create New Day"
    form = DayForm()
    form.submit.label.text = "Create Day"

    if form.validate_on_submit():
        order_num = get_next_day_order()

        new_day = Day(name=form.name.data, abbreviation=form.abbreviation.data, description=form.description.data, order=order_num)

        db.session.add(new_day)
        db.session.commit()

        flash("Day added.", "success")
        return redirect(url_for("calendar.settings"))

    return render_template("calendar/form.html", form=form, heading=heading, title=page_title("Create new day"))

@bp.route("/day/edit/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required(no_perm_url)
def day_edit(id):
    heading = "Edit Day"
    form = DayForm()
    form.submit.label.text = "Save Day"

    day = Day.query.filter_by(id=id).first_or_404()

    if form.validate_on_submit():
        day.name = form.name.data
        day.abbreviation = form.abbreviation.data
        day.description = form.description.data

        db.session.commit()

        flash("Day edited.", "success")
        return redirect(url_for("calendar.settings"))
    elif request.method == "GET":
        form.name.data = day.name
        form.abbreviation.data = day.abbreviation
        form.description.data = day.description

    return render_template("calendar/form.html", item=day, form=form, heading=heading, title=page_title("Edit day '%s'" % day.name))

@bp.route("/day/delete/<int:id>", methods=["GET"])
@login_required
@admin_required(no_perm_url)
def day_delete(id):
    cset = CalendarSetting.query.get(1)
    if cset.finalized == True:
        flash("The calendar is finalized. You can't delete days.", "danger")
        return redirect(url_for('calendar.settings'))

    day = Day.query.filter_by(id=id).first_or_404()

    db.session.delete(day)
    db.session.commit()

    flash("Day was deleted.", "success")
    return redirect(url_for("calendar.settings"))


@bp.route("/day/up/<int:id>", methods=["GET"])
@login_required
@admin_required(no_perm_url)
def day_up(id):
    cset = CalendarSetting.query.get(1)
    if cset.finalized == True:
        flash("The calendar is finalized. You can't change the order of days.", "danger")
        return redirect(url_for('calendar.settings'))

    day_to_up = Day.query.filter_by(id=id).first_or_404()
    day_to_down = Day.query.filter(Day.order < day_to_up.order).order_by(Day.order.desc()).limit(1).first()

    if not day_to_down:
        flash("No day with lower order found.", "danger")
        return redirect(url_for("calendar.settings"))

    up_order = day_to_up.order
    down_order = day_to_down.order

    day_to_up.order = down_order
    day_to_down.order = up_order

    db.session.commit()

    flash("Order of '" + day_to_up.name + "' and '" + day_to_down.name + "' has been swapped.", "success")
    return redirect(url_for("calendar.settings"))

@bp.route("/day/down/<int:id>", methods=["GET"])
@login_required
@admin_required(no_perm_url)
def day_down(id):
    cset = CalendarSetting.query.get(1)
    if cset.finalized == True:
        flash("The calendar is finalized. You can't change the order of days.", "danger")
        return redirect(url_for('calendar.settings'))

    day_to_down = Day.query.filter_by(id=id).first_or_404()
    day_to_up = Day.query.filter(Day.order > day_to_down.order).order_by(Day.order.asc()).limit(1).first()

    if not day_to_up:
        flash("No day with higher order found.", "danger")
        return redirect(url_for("calendar.settings"))

    down_order = day_to_down.order
    up_order = day_to_up.order

    day_to_down.order = up_order
    day_to_up.order = down_order

    db.session.commit()

    flash("Order of '" + day_to_down.name + "' and '" + day_to_up.name + "' has been swapped.", "success")
    return redirect(url_for("calendar.settings"))

@bp.route("/moon/create", methods=["GET", "POST"])
@login_required
@admin_required(no_perm_url)
def moon_create():
    cset = CalendarSetting.query.get(1)
    if cset.finalized == True:
        flash("The calendar is finalized. You can't add new moons.", "danger")
        return redirect(url_for('calendar.settings'))

    heading = "Create New Moon"
    form = MoonForm()
    form.submit.label.text = "Create Moon"

    if form.validate_on_submit():
        new_moon = Moon(name=form.name.data, description=form.description.data, phase_length=form.phase_length.data, phase_offset=form.phase_offset.data, waxing_color=stretch_color(form.waxing_color.data.hex), waning_color=stretch_color(form.waning_color.data.hex))

        db.session.add(new_moon)
        db.session.commit()

        flash("Moon added.", "success")
        return redirect(url_for("calendar.settings"))

    return render_template("calendar/form.html", form=form, heading=heading, title=page_title("Create new moon"))

@bp.route("/moon/edit/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required(no_perm_url)
def moon_edit(id):
    heading = "Edit Moon"
    form = MoonForm()
    form.submit.label.text = "Save Moon"

    moon = Moon.query.filter_by(id=id).first_or_404()

    if form.validate_on_submit():
        moon.name = form.name.data
        moon.description = form.description.data
        moon.phase_length = form.phase_length.data
        moon.phase_offset = form.phase_offset.data
        moon.waxing_color = stretch_color(form.waxing_color.data.hex)
        moon.waning_color = stretch_color(form.waning_color.data.hex)
        db.session.commit()

        flash("Moon edited.", "success")
        return redirect(url_for("calendar.settings"))
    elif request.method == "GET":
        form.name.data = moon.name
        form.description.data = moon.description
        form.phase_length.data = moon.phase_length
        form.phase_offset.data = moon.phase_offset
        form.waxing_color.data = moon.waxing_color
        form.waning_color.data = moon.waning_color

    return render_template("calendar/form.html", item=moon, form=form, heading=heading, title=page_title("Edit moon '%s'" % moon.name))

@bp.route("/moon/delete/<int:id>", methods=["GET"])
@login_required
@admin_required(no_perm_url)
def moon_delete(id):
    cset = CalendarSetting.query.get(1)
    if cset.finalized == True:
        flash("The calendar is finalized. You can't delete days.", "danger")
        return redirect(url_for('calendar.settings'))

    moon = Moon.query.filter_by(id=id).first_or_404()

    db.session.delete(moon)
    db.session.commit()

    flash("Moon was deleted.", "success")
    return redirect(url_for("calendar.settings"))