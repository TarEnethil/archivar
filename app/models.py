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

    def has_special_role(self):
        return self.has_role(5)

    def is_map_admin(self):
        return self.has_admin_role() or self.has_map_role()

    def is_wiki_admin(self):
        return self.has_admin_role() or self.has_wiki_role()

    def is_event_admin(self):
        return self.has_admin_role() or self.has_event_role()

    def has_access_to_some_settings(self):
        return self.has_admin_role() or self.has_map_role() or self.has_wiki_role()

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
            "created_by" : self.created_by.username
        }

        if (self.edited_by):
            dic["edited"] = self.edited,
            dic["edited_by"] = self.edited_by.username

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

@login.user_loader
def load_user(id):
    return User.query.get(int(id))