from app import db
from app.helpers import urlfriendly
from app.calendar.models import Day, Month, Epoch
from app.mixins import LinkGenerator, SimpleChangeTracker, SimplePermissionChecker
from flask import url_for
from flask_login import current_user
from jinja2 import Markup


class EventSetting(db.Model, SimpleChangeTracker):
    __tablename__ = "event_settings"
    id = db.Column(db.Integer, primary_key=True)
    default_category = db.Column(db.Integer, db.ForeignKey("event_categories.id"))
    default_epoch = db.Column(db.Integer, db.ForeignKey("epochs.id"))
    default_year = db.Column(db.Integer)


class EventCategory(db.Model, SimpleChangeTracker, LinkGenerator):
    __tablename__ = "event_categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    color = db.Column(db.String(10))

    def get_events(self):
        return list(filter(lambda x: x.is_viewable_by_user(), self.events))

    #####
    # LinkGenerator functions
    #####
    def view_text(self):
        return Markup(f'<span style="color:{self.color};">█</span> {self.name}')

    def view_url(self):
        return url_for('event.list_category', c_id=self.id, c_name=urlfriendly(self.name))

    def edit_url(self):
        return url_for('event.category_edit', id=self.id, name=urlfriendly(self.name))


class Event(db.Model, SimplePermissionChecker, LinkGenerator):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    category_id = db.Column(db.Integer, db.ForeignKey("event_categories.id"))
    category = db.relationship("EventCategory", backref="events")
    description = db.Column(db.Text)
    epoch_id = db.Column(db.Integer, db.ForeignKey("epochs.id"))
    epoch = db.relationship("Epoch", backref="events")
    year = db.Column(db.Integer)
    month_id = db.Column(db.Integer, db.ForeignKey("months.id"))
    month = db.relationship("Month")
    day = db.Column(db.Integer)
    timestamp = db.Column(db.Integer)
    duration = db.Column(db.Integer)

    def format_date(self, epoch, year, month, day, timestamp, use_abbr,
                    with_link=False, use_epoch=True, use_year=True, with_weekday=False):
        from app.helpers import urlfriendly
        day_str = str(day)

        if with_weekday:
            day_str = f"{self.day_of_the_week(timestamp)}, {day_str}"

        month_str = month.abbreviation if use_abbr and month.abbreviation else month.name

        if with_link:
            url = url_for('event.list_epoch_year', e_id=epoch.id, year=year, e_name=urlfriendly(epoch.name))
            year_str = f'<a href="{url}">{year}</a>'
        else:
            year_str = str(year)

        epoch_str = epoch.abbreviation if use_abbr and epoch.abbreviation else epoch.name

        if with_link:
            url = url_for('event.list_epoch', e_id=epoch.id, e_name=urlfriendly(epoch.name))
            epoch_str = f'<a href="{url}">{epoch_str}</a>'

        if use_epoch and use_year:
            return f'{day_str}. {month_str} {year_str}, {epoch_str}'
        elif use_year and not use_epoch:
            return f'{day_str}. {month_str} {year_str}'

        return f'{day_str}. {month_str}'

    def start_date(self, use_abbr, with_link=False, use_epoch=True, use_year=True, with_weekday=False):
        return self.format_date(self.epoch, self.year, self.month, self.day, self.timestamp,
                                use_abbr, with_link, use_epoch, use_year, with_weekday)

    def end_date(self, use_abbr, with_link=False, use_epoch=True, use_year=True, with_weekday=False):
        # timestamp of end-date
        timestamp = self.timestamp + self.duration

        epochs = Epoch.query.order_by(Epoch.order.asc()).all()
        months = Month.query.order_by(Month.order.asc()).all()
        days_per_year = months[-1].days_before + months[-1].days

        # find epoch
        total_years = int(timestamp / days_per_year)
        epoch_idx = -1

        for i, e in enumerate(epochs):
            if total_years < e.years_before:
                epoch_idx = max(0, i - 1)
                break

        epoch = epochs[epoch_idx]

        # find year
        year = total_years - epoch.years_before + 1

        # find month
        days_into_year = timestamp - (days_per_year * total_years)
        month_idx = -1

        for i, m in enumerate(months):
            if days_into_year < m.days_before:
                month_idx = max(0, i - 1)
                break

        month = months[month_idx]

        # find day
        day = days_into_year - month.days_before

        return self.format_date(epoch, year, month, day, timestamp, use_abbr, with_link, use_epoch, use_year,
                                with_weekday)

    def day_of_the_week(self, timestamp=None):
        wd = Day.query.order_by(Day.order.asc()).all()

        if timestamp is None:
            return wd[(self.timestamp % len(wd)) - 1].name
        else:
            return wd[(timestamp % len(wd)) - 1].name

    #####
    # Permissions
    #####
    def is_viewable_by_user(self):
        return self.is_visible or self.is_owned_by_user()

    def is_editable_by_user(self):
        return self.is_visible or self.is_owned_by_user()

    def is_deletable_by_user(self):
        return self.is_owned_by_user() or (self.is_visible and current_user.is_at_least_moderator())

    #####
    # LinkGenerator functions
    #####
    def view_text(self):
        return self.name

    def view_url(self):
        return url_for('event.view', id=self.id, name=urlfriendly(self.name))

    def edit_url(self):
        return url_for('event.edit', id=self.id, name=urlfriendly(self.name))

    def delete_url(self):
        return url_for('event.delete', id=self.id, name=urlfriendly(self.name))
