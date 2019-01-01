from app import db, login
from flask import url_for
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

user_role_assoc = db.Table("user_role_assoc",
                    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
                    db.Column("role_id", db.Integer, db.ForeignKey("roles.id")))

character_party_assoc = db.Table("character_party_assoc",
                    db.Column("character_id", db.Integer, db.ForeignKey("characters.id")),
                    db.Column("party_id", db.Integer, db.ForeignKey("parties.id")))

session_character_assoc = db.Table("session_character_assoc",
                    db.Column("session_id", db.Integer, db.ForeignKey("sessions.id")),
                    db.Column("character_id", db.Integer, db.ForeignKey("characters.id")))

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about = db.Column(db.String(1000))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    must_change_password = db.Column(db.Boolean, default=True)

    roles = db.relationship("Role", secondary=user_role_assoc, backref="users")
    characters = db.relationship("Character", backref="user")

    dateformat = db.Column(db.String(25), default="LLL")
    phb_session = db.Column(db.Boolean, default=False)
    phb_wiki = db.Column(db.Boolean, default=False)
    phb_character = db.Column(db.Boolean, default=False)
    phb_party = db.Column(db.Boolean, default=False)
    phb_calendar = db.Column(db.Boolean, default=False)

    def has_role(self, roleId):
        role = Role.query.get(roleId)

        return role in self.roles

    def has_admin_role(self):
        return self.has_role(1)

    def has_map_role(self):
        return self.has_role(2)

    def has_wiki_role(self):
        return self.has_role(3)

    def has_event_role(self):
        return self.has_role(4)

    def has_media_role(self):
        return self.has_role(5)

    def has_special_role(self):
        return self.has_role(6)

    def is_map_admin(self):
        return self.has_admin_role() or self.has_map_role()

    def is_wiki_admin(self):
        return self.has_admin_role() or self.has_wiki_role()

    def is_event_admin(self):
        return self.has_admin_role() or self.has_event_role()

    def is_media_admin(self):
        return self.has_admin_role() or self.has_media_role()

    def has_access_to_some_settings(self):
        return self.has_admin_role() or self.has_map_role() or self.has_wiki_role() or self.has_event_role() or self.has_media_role()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    description = db.Column(db.String(256))

class GeneralSetting(db.Model):
    __tablename__ = "general_settings"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    world_name = db.Column(db.String(64))
    welcome_page = db.Column(db.Text)
    quicklinks = db.Column(db.Text)

class MapSetting(db.Model):
    __tablename__ = "map_settings"
    id = db.Column(db.Integer, primary_key=True)
    min_zoom = db.Column(db.Integer)
    max_zoom = db.Column(db.Integer)
    default_zoom = db.Column(db.Integer)
    icon_anchor = db.Column(db.Integer)
    tiles_path = db.Column(db.String(128), default="tile_{z}_{x}-{y}.png")
    external_provider = db.Column(db.Boolean, default=False)
    default_visible = db.Column(db.Boolean, default=False)

class MapNodeType(db.Model):
    __tablename__ = "map_node_types"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.String(256))
    icon_file = db.Column(db.String(64))
    icon_width = db.Column(db.Integer)
    icon_height = db.Column(db.Integer)

    def to_dict(self):
        dic = {
            "id" : self.id,
            "name" : self.name,
            "description" : self.description,
            "icon_file" : url_for("map.node_type_icon", filename=self.icon_file),
            "icon_width": self.icon_width,
            "icon_height": self.icon_height
        }

        return dic

class MapNode(db.Model):
    __tablename__ = "map_nodes"
    id = db.Column(db.Integer, primary_key=True)
    coord_x = db.Column(db.Float)
    coord_y = db.Column(db.Float)
    name = db.Column(db.String(64))
    description = db.Column(db.String(10000))
    node_type = db.Column(db.Integer, db.ForeignKey("map_node_types.id"))
    is_visible = db.Column(db.Boolean, default=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_by = db.relationship("User", foreign_keys=[created_by_id])
    edited = db.Column(db.DateTime, default=datetime.utcnow)
    edited_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    edited_by = db.relationship("User", foreign_keys=[edited_by_id])
    wiki_entry_id = db.Column(db.Integer, db.ForeignKey("wiki_entries.id"), default=0)

    def to_dict(self):
        dic = {
            "id" : self.id,
            "x" : self.coord_x,
            "y" : self.coord_y,
            "name" : self.name,
            "desc" : self.description,
            "node_type" : self.node_type,
            "visible" : self.is_visible,
            "created" : self.created,
            "created_by" : self.created_by.username,
            "wiki_id" : self.wiki_entry_id
        }

        if self.edited_by:
            # do update here because otherwise, this lands in a list of length one for some reason
            dic.update({
                "edited" : self.edited,
                "edited_by" : self.edited_by.username
            })

        return dic

class Character(db.Model):
    __tablename__ = "characters"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    player = db.relationship("User")

    created = db.Column(db.DateTime, default=datetime.utcnow)
    edited = db.Column(db.DateTime, default=datetime.utcnow)

    parties = db.relationship("Party", secondary=character_party_assoc, backref="members")

    name = db.Column(db.String(250))
    race = db.Column(db.String(100))
    class_ = db.Column(db.String(100))
    description = db.Column(db.Text)
    dm_notes = db.Column(db.Text)

class Party(db.Model):
    __tablename__ = "parties"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    dm_notes = db.Column(db.Text)

class Session(db.Model):
    __tablename__ = "sessions"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    summary = db.Column(db.Text)
    code = db.Column(db.String(3))
    dm_notes = db.Column(db.Text)
    date = db.Column(db.DateTime)
    participants = db.relationship("Character", secondary=session_character_assoc, backref="sessions")

class WikiSetting(db.Model):
    __tablename__ = "wiki_settings"
    id = db.Column(db.Integer, primary_key=True)
    default_visible = db.Column(db.Boolean, default=False)

class WikiEntry(db.Model):
    __tablename__ = "wiki_entries"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_by = db.relationship("User", foreign_keys=[created_by_id])
    edited = db.Column(db.DateTime, default=datetime.utcnow)
    edited_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    edited_by = db.relationship("User", foreign_keys=[edited_by_id])

    title = db.Column(db.String(255))
    category = db.Column(db.String(100))
    is_visible = db.Column(db.Boolean)
    content = db.Column(db.Text)
    dm_content = db.Column(db.Text)
    tags = db.Column(db.String(255))

    def split_tags(self):
        return self.tags.split(" ")

class CalendarSetting(db.Model):
    __tablename__ = "calendar_settings"
    id = db.Column(db.Integer, primary_key=True)
    finalized = db.Column(db.Boolean, default=False)

class Epoch(db.Model):
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
            "name" : self.name,
            "abbr" : self.abbreviation,
            "description" : self.description,
            "years" : self.years,
            "circa" : self.circa
        }

        if self.years_before != 0 and self.years_before != None:
            dic["years_before"] = self.years_before

        return dic

    def __repr__(self):
        return str(self.to_dict())

class Month(db.Model):
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
            "name" : self.name,
            "abbr" : self.abbreviation,
            "description" : self.description,
            "days" : self.days
        }

        if self.days_before != 0 and self.days_before != None:
            dic["days_before"] = self.days_before

        return dic

    def __repr__(self):
        return str(self.to_dict())

class Day(db.Model):
    __tablename__ = "days"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    abbreviation = db.Column(db.String(5))
    description = db.Column(db.Text)
    order = db.Column(db.Integer)

    def to_dict(self):
        dic = {
            "name" : self.name,
            "abbr" : self.abbreviation,
            "description" : self.description
        }

        return dic

    def __repr__(self):
        return str(self.to_dict())

class Moon(db.Model):
    __tablename__ = "moons"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    phase_length = db.Column(db.Integer)
    phase_offset = db.Column(db.Integer)

class EventSetting(db.Model):
    __tablename__ = "event_settings"
    id = db.Column(db.Integer, primary_key=True)
    default_visible = db.Column(db.Boolean)
    default_category = db.Column(db.Integer, db.ForeignKey("event_categories.id"))
    default_epoch = db.Column(db.Integer, db.ForeignKey("epochs.id"))
    default_year = db.Column(db.Integer)

class EventCategory(db.Model):
    __tablename__ = "event_categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    color = db.Column(db.String(10))

class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    is_visible = db.Column(db.Boolean)
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

    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_by = db.relationship("User", foreign_keys=[created_by_id])
    edited_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    edited_by = db.relationship("User", foreign_keys=[edited_by_id])

    def format_date(self, epoch, year, month, day, timestamp, use_abbr, with_link=False, use_epoch=True, use_year=True, with_weekday=False):
        day_str = str(day)

        if with_weekday:
            day_str = self.day_of_the_week(timestamp) + ", " + day_str

        month_str = month.abbreviation if use_abbr and month.abbreviation else month.name
        year_str = '<a href="{0}">{1}</a>'.format(url_for('event.list_epoch_year', e_id=epoch.id, year=year), year) if with_link else str(year)
        epoch_str = epoch.abbreviation if use_abbr and epoch.abbreviation else epoch.name
        epoch_str = '<a href="{0}">{1}</a>'.format(url_for('event.list_epoch', e_id=epoch.id), epoch_str) if with_link else epoch_str

        if use_epoch and use_year:
            return '{0}. {1} {2}, {3}'.format(day_str, month_str, year_str, epoch_str)
        elif use_year and not use_epoch:
            return '{0}. {1} {2}'.format(day_str, month_str, year_str)

        return '{0}. {1}'.format(day_str, month_str)

    def start_date(self, use_abbr, with_link=False, use_epoch=True, use_year=True, with_weekday=False):
        return self.format_date(self.epoch, self.year, self.month, self.day, self.timestamp, use_abbr, with_link, use_epoch, use_year, with_weekday)

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

        return self.format_date(epoch, year, month, day, timestamp, use_abbr, with_link, use_epoch, use_year, with_weekday)

    def day_of_the_week(self, timestamp=None):
        wd = Day.query.order_by(Day.order.asc()).all()

        if timestamp == None:
            return wd[(self.timestamp % len(wd)) - 1].name
        else:
            return wd[(timestamp % len(wd)) -1].name

class MediaSetting(db.Model):
    __tablename__ = "media_settings"
    id = db.Column(db.Integer, primary_key=True)
    default_visible = db.Column(db.Boolean)

class MediaCategory(db.Model):
    __tablename__ = "media_categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def to_dict(self):
        dic = {
            "id" : self.id,
            "name" : self.name,
        }

        return dic

class MediaItem(db.Model):
    __tablename__ = "media"
    id = db.Column(db.Integer, primary_key=True)
    is_visible = db.Column(db.Boolean)
    name = db.Column(db.String(100))
    filename = db.Column(db.String(100))
    filesize = db.Column(db.Integer)
    category_id = db.Column(db.Integer, db.ForeignKey("media_categories.id"))
    category = db.relationship("MediaCategory", backref="events")

    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_by = db.relationship("User", foreign_keys=[created_by_id])
    edited_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    edited_by = db.relationship("User", foreign_keys=[edited_by_id])

    def get_file_ext(self):
        return (self.filename.split(".")[-1]).lower()

    def to_dict(self):
        dic = {
            "id" : self.id,
            "name" : self.name,
            "filename" : self.filename,
            "filesize" : self.filesize,
            "category" : self.category_id,
            "file_ext" : self.get_file_ext(),
            "is_visible" : self.is_visible
        }

        return dic

@login.user_loader
def load_user(id):
    return User.query.get(int(id))