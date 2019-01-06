from app import db
from app.helpers import flash_no_permission
from app.models import Event, EventCategory, Role, User
from app.calendar.helpers import gen_calendar_stats
from flask_login import current_user
from sqlalchemy import and_, or_, not_

# check if current user is event admin
def redirect_non_event_admins():
    if not current_user.is_event_admin():
        flash_no_permission()
        return True
    return False

# generate choices for event category SelectField
def gen_event_category_choices():
    choices = []

    categories = EventCategory.query.all()

    for cat in categories:
        choices.append((cat.id, cat.name))

    return choices

# get all event categories
def get_event_categories():
    q = EventCategory.query.order_by(EventCategory.id.asc()).all()

    return q

# (re)calculate the timestamp for an event
def update_timestamp(event_id):
    timestamp = 0
    ev = Event.query.filter_by(id=event_id).first()
    stats = gen_calendar_stats()

    if ev == None:
        return

    years = ev.epoch.years_before + (ev.year - 1)

    days_into_year = ev.month.days_before + ev.day

    timestamp = years * stats["days_per_year"] + days_into_year

    ev.timestamp = timestamp
    db.session.commit()

# get events by epoch and/or year
def get_events(filter_epoch=None, filter_year=None):
    if current_user.has_admin_role():
        events = Event.query
    elif current_user.has_event_role():
        admins = User.query.filter(User.roles.contains(Role.query.get(1)))
        admin_ids = [a.id for a in admins]
        events = Event.query.filter(not_(and_(Event.is_visible == False, Event.created_by_id.in_(admin_ids))))
    else:
        events = Event.query.filter(or_(Event.is_visible == True, Event.created_by_id == current_user.id))

    if filter_epoch and filter_year:
        events = events.filter_by(epoch_id = filter_epoch, year = filter_year)
    elif filter_epoch:
        events = events.filter_by(epoch_id = filter_epoch)

    events = events.order_by(Event.timestamp.asc()).all()

    return events

# get all events for the specified category
def get_events_by_category(category_id):
    if current_user.has_admin_role():
        events = Event.query
    elif current_user.has_event_role():
        admins = User.query.filter(User.roles.contains(Role.query.get(1)))
        admin_ids = [a.id for a in admins]
        events = Event.query.filter(not_(and_(Event.is_visible == False, Event.created_by_id.in_(admin_ids))))
    else:
        events = Event.query.filter(or_(Event.is_visible == True, Event.created_by_id == current_user.id))

    events = events.filter_by(category_id = category_id)

    events = events.order_by(Event.timestamp.asc()).all()

    return events