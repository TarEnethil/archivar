from app import db
from app.models import CalendarSetting, Day, Epoch, Event, EventCategory, Month, Moon
from flask import flash

# get highest order num for newly created epoch
def get_next_epoch_order():
    q = Epoch.query.order_by(Epoch.order.desc()).limit(1).first()

    if q:
        return q.order + 1
    else:
        return 1

# get highest order num for newly created month
def get_next_month_order():
    q = Month.query.order_by(Month.order.desc()).limit(1).first()

    if q:
        return q.order + 1
    else:
        return 1

# def get highest order num for newly created day
def get_next_day_order():
    q = Day.query.order_by(Day.order.desc()).limit(1).first()

    if q:
        return q.order + 1
    else:
        return 1

# check constraints
# contraints:
# - at least one epoch, month and day
# - only the epoch with the highest order (current epoch) can have duration 0
def calendar_sanity_check():
    tests_passed = True

    cset = CalendarSetting.query.get(1)

    if cset.finalized == True:
        tests_passed = False
        flash("The calendar is already finalized.", "danger")

    epochs = Epoch.query.all()

    if not epochs:
        tests_passed = False
        flash("Calendar needs at least one epoch.", "danger")
    else:
        current_epoch = Epoch.query.order_by(Epoch.order.desc()).limit(1).first()

        if current_epoch.years != 0:
            tests_passed = False
            flash("The current epoch (" + current_epoch.name + ") needs a duration of 0.", "danger")

        all_other_epochs = Epoch.query.filter(Epoch.id != current_epoch.id).all()

        for epoch in all_other_epochs:
            if epoch.years == 0:
                tests_passed = False
                flash("All epochs except the current one need a duration > 0. '" + epoch.name + "' violates that constraint." , "danger")

    months = Month.query.all()

    if not months:
        tests_passed = False
        flash("Calendar needs at least one month.", "danger")

    days = Day.query.all()

    if not days:
        tests_passed = False
        flash("Calendar needs at least one day.", "danger")

    return tests_passed

# generate dict containing all info for the calendar preview
# can be used to commit to database
def gen_calendar_preview_data(commit=False):
    epochs = Epoch.query.order_by(Epoch.order.asc()).all()
    months = Month.query.order_by(Month.order.asc()).all()
    days = Day.query.order_by(Day.order.asc()).all()
    moons = Moon.query.order_by(Moon.name.asc()).all()

    for i, epoch in enumerate(epochs):
        if i > 0:
            epoch.years_before = epochs[i - 1].years_before + epochs[i - 1].years

    for i, month in enumerate(months):
        if i > 0:
            month.days_before = months[i - 1].days_before + months[i - 1].days

    if commit == True:
        db.session.commit()
    else:
        preview_info = {}
        preview_info["epochs"] = epochs
        preview_info["months"] = months
        preview_info["days"] = days

        preview_info["days_per_week"] = len(days)
        preview_info["days_per_year"] = months[-1].days_before + months[-1].days
        preview_info["months_per_year"] = len(months)

        if moons:
            preview_info["moons"] = moons

        return preview_info

# generate dict containing all info for the calendar
def gen_calendar_stats():
    epochs = Epoch.query.order_by(Epoch.order.asc()).all()
    months = Month.query.order_by(Month.order.asc()).all()
    days = Day.query.order_by(Day.order.asc()).all()
    categories = EventCategory.query.all()
    moons = Moon.query.order_by(Moon.name.asc()).all()

    stats = {}
    stats["epochs"] = epochs
    stats["months"] = months
    stats["days"] = days
    stats["categories"] = categories

    stats["days_per_week"] = len(days)
    stats["days_per_year"] = months[-1].days_before + months[-1].days
    stats["months_per_year"] = len(months)

    if moons:
        stats["moons"] = moons

    return stats

# generate choices for epoch SelectField
def gen_epoch_choices():
    return [(e.id, e.name) for e in Epoch.query.order_by(Epoch.order.asc()).all()]

# generate choices for month SelectField
def gen_month_choices():
    return [(m.id, m.name) for m in Month.query.order_by(Month.order.asc()).all()]

# generate choices for the days of a specified month
def gen_day_choices(month_id):
    m = Month.query.filter_by(id=month_id).first()

    if m == None:
        return ([0, "ERROR month not found"])

    return [(n, n) for n in range(1, m.days + 1)]

# get all epochs by order
def get_epochs():
    e = Epoch.query.order_by(Epoch.order.asc()).all()

    return e

# get all years in an epoch that have events
def get_years_in_epoch(e_id):
    q = Event.query.with_entities(Event.year).filter_by(epoch_id=e_id).group_by(Event.year).order_by(Event.year.asc()).all()

    return q