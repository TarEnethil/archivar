from app import db
from app.event.models import Event, EventCategory
from app.calendar.helpers import gen_calendar_stats


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

    if ev is None:
        return

    years = ev.epoch.years_before + (ev.year - 1)

    days_into_year = ev.month.days_before + ev.day

    timestamp = years * stats["days_per_year"] + days_into_year

    ev.timestamp = timestamp
    db.session.commit()


# get events by epoch and/or year
def get_events(filter_epoch=None, filter_year=None):
    events = Event.get_query_for_visible_items(include_hidden_for_user=True)

    if filter_epoch and filter_year:
        events = events.filter_by(epoch_id=filter_epoch, year=filter_year)
    elif filter_epoch:
        events = events.filter_by(epoch_id=filter_epoch)

    events = events.order_by(Event.timestamp.asc()).all()

    return events


# get all events for the specified category
def get_events_by_category(category_id):
    events = Event.get_query_for_visible_items(include_hidden_for_user=True)
    events = events.filter_by(category_id=category_id)
    events = events.order_by(Event.timestamp.asc()).all()

    return events
