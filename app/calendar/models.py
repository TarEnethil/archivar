from app import db
from app.helpers import urlfriendly
from app.mixins import LinkGenerator, SimpleChangeTracker
from flask import url_for
from jinja2 import Markup


class CalendarSetting(db.Model, SimpleChangeTracker):
    __tablename__ = "calendar_settings"
    id = db.Column(db.Integer, primary_key=True)
    finalized = db.Column(db.Boolean, default=False)


class Epoch(db.Model, SimpleChangeTracker, LinkGenerator):
    __tablename__ = "epochs"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    abbreviation = db.Column(db.String(5))
    description = db.Column(db.Text)
    circa = db.Column(db.Boolean, default=False)
    years = db.Column(db.Integer)
    order = db.Column(db.Integer)
    years_before = db.Column(db.Integer, default=0)

    def to_dict(self):
        dic = {
            "name": self.name,
            "abbr": self.abbreviation,
            "description": self.description,
            "years": self.years,
            "circa": self.circa
        }

        if self.years_before != 0 and self.years_before is not None:
            dic["years_before"] = self.years_before

        return dic

    def __repr__(self):
        return str(self.to_dict())

    #####
    # LinkGenerator functions
    #####
    def edit_url(self):
        return url_for('calendar.epoch_edit', id=self.id, name=urlfriendly(self.name))

    def delete_url(self):
        return url_for('calendar.epoch_delete', id=self.id, name=urlfriendly(self.name))


class Month(db.Model, SimpleChangeTracker, LinkGenerator):
    __tablename__ = "months"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    abbreviation = db.Column(db.String(5))
    description = db.Column(db.Text)
    days = db.Column(db.Integer)
    order = db.Column(db.Integer)
    days_before = db.Column(db.Integer, default=0)

    def to_dict(self):
        dic = {
            "name": self.name,
            "abbr": self.abbreviation,
            "description": self.description,
            "days": self.days
        }

        if self.days_before != 0 and self.days_before is not None:
            dic["days_before"] = self.days_before

        return dic

    def __repr__(self):
        return str(self.to_dict())

    #####
    # LinkGenerator functions
    #####
    def edit_url(self):
        return url_for('calendar.month_edit', id=self.id, name=urlfriendly(self.name))

    def delete_url(self):
        return url_for('calendar.month_delete', id=self.id, name=urlfriendly(self.name))


class Day(db.Model, SimpleChangeTracker, LinkGenerator):
    __tablename__ = "days"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    abbreviation = db.Column(db.String(5))
    description = db.Column(db.Text)
    order = db.Column(db.Integer)

    def to_dict(self):
        dic = {
            "name": self.name,
            "abbr": self.abbreviation,
            "description": self.description
        }

        return dic

    def __repr__(self):
        return str(self.to_dict())

    #####
    # LinkGenerator functions
    #####
    def edit_url(self):
        return url_for('calendar.day_edit', id=self.id, name=urlfriendly(self.name))

    def delete_url(self):
        return url_for('calendar.day_delete', id=self.id, name=urlfriendly(self.name))


class Moon(db.Model, SimpleChangeTracker, LinkGenerator):
    __tablename__ = "moons"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    phase_length = db.Column(db.Integer)
    phase_offset = db.Column(db.Integer)
    waxing_color = db.Column(db.String(10))
    waning_color = db.Column(db.String(10))
    color = db.Column(db.String(10))
    delta = 2  # max phase deviation

    def calc_phase(self, timestamp):
        return (((timestamp + self.phase_offset - 1) % self.phase_length) / float(self.phase_length))

    def phase_name(self, phase):
        phase *= 100

        if (phase >= 50 - self.delta) and (phase <= 50 + self.delta):
            return "New Moon"

        if phase <= 0 + self.delta:
            return "Full moon"
        elif phase < 25 - self.delta:
            return "Waning gibbous"
        elif phase <= 25 + self.delta:
            return "Third quarter"
        elif phase < 50 - self.delta:
            return "Waning crescent"
        elif phase < 75 - self.delta:
            return "Waxing crescent"
        elif phase <= 75 + self.delta:
            return "First quarter"
        elif phase < 100 - self.delta:
            return "Waxing gibbous"
        else:
            return "Full moon"

    # this was a nice and elegant functions once
    def print_phase(self, timestamp, moon_size=50, print_name=False, print_phase=False):
        phase_percent = self.calc_phase(timestamp)
        name = ""
        phase_name = self.phase_name(phase_percent)
        phase_name_span = ""
        spread = 0
        moon_div = ""
        normal_moon_div = '<div class="moon" style="transform:rotate({0}deg);box-shadow:inset \
                           {1}px 0 0px {2}px {3}; background:{4};"></div>'
        half_moon_div = '<span class="half-moon" style="background:{0};width:{1}px;{2};{3};"></span>'

        if print_name:
            name = f'<span class="moon-text">{self.name}</span>'

        if print_phase:
            phase_name_span = f'<span class="moon-text">{phase_name}</span>'

        # defaults for falling moon
        transform = 0
        shadow_size = 0
        shadow_color = self.waning_color
        moon_color = "#444"
        align = ""

        # new moon: display nothing
        if 50 - self.delta <= (phase_percent * 100) <= 50 + self.delta:
            moon_div = '<div class="moon"></div>'
        elif phase_percent > 0.5:  # rising moon
            # exactly half moon
            if 75 - self.delta <= (phase_percent * 100) <= 75 + self.delta:
                size = moon_size - 4  # moon_size - 2 * padding
                border1 = f"border-top-right-radius:{size}px"
                border2 = f"border-bottom-right-radius:{size}px"
                moon_div = half_moon_div.format(self.waxing_color, size / 2, border1, border2)
                align = "text-align:right;"
            else:  # every other rising moon
                transform = 180
                shadow_size = (phase_percent - 0.5) * 2 * moon_size
                shadow_color = self.waxing_color
                spread = int((moon_size / -7) * 4 * (0.25 - abs(0.75 - phase_percent)))

                # from half moon to new moon, swap colors and transform
                if phase_percent * 100 > 75 + self.delta:
                    transform = 0
                    moon_color = self.waxing_color
                    shadow_color = "#444"
                    shadow_size = moon_size - shadow_size

                moon_div = normal_moon_div.format(transform, shadow_size, spread, shadow_color, moon_color)
        else:  # falling moon
            # exactly half moon
            if 25 - self.delta <= (phase_percent * 100) <= 25 + self.delta:
                size = moon_size - 4  # moon_size - 2 * padding
                border1 = f"border-top-left-radius:{size}px"
                border2 = f"border-bottom-left-radius:{size}px"
                moon_div = half_moon_div.format(self.waning_color, size / 2, border1, border2)
                align = "text-align:left;"
            else:  # every other falling moon
                shadow = moon_size - (phase_percent * 2 * moon_size)
                spread = int((moon_size / -7) * 4 * (0.25 - abs(0.25 - phase_percent)))

                # from new moon and half moon, swap colors and transform
                if 0 + self.delta < phase_percent * 100 < 25 - self.delta:
                    transform = 180
                    shadow_color = "#444"
                    moon_color = self.waning_color
                    shadow = moon_size - shadow

                moon_div = normal_moon_div.format(transform, shadow, spread, shadow_color, moon_color)

        wrap = f'<div class="moon-wrap" style="width:{moon_size}px;height:{moon_size}px;{align}">{moon_div}</div>'
        div = f'<div class="moon-box" title="{phase_name} ({phase_percent:4.3f})">{name}{wrap}{phase_name_span}</div>'
        return Markup(div)

    def print_phases(self, moon_size=50, print_name=False, print_phase=False):
        out = ""
        for x in range(self.phase_length):
            out += f"{self.print_phase(x + 1, moon_size, print_name, print_phase)}\n"

        return out

    #####
    # LinkGenerator functions
    #####
    def edit_url(self):
        return url_for('calendar.moon_edit', id=self.id, name=urlfriendly(self.name))

    def delete_url(self):
        return url_for('calendar.moon_delete', id=self.id, name=urlfriendly(self.name))
