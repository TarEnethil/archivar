from app import db, login
from app.mixins import LinkGenerator
from datetime import datetime
from flask import url_for, current_app
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

user_role_assoc = db.Table("user_role_assoc",
                            db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
                            db.Column("role_id", db.Integer, db.ForeignKey("roles.id")))

class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    description = db.Column(db.String(256))

class User(UserMixin, db.Model, LinkGenerator):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about = db.Column(db.String(1000))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    must_change_password = db.Column(db.Boolean, default=True)

    created = db.Column(db.DateTime, default=datetime.utcnow)
    edited = db.Column(db.DateTime, default=None, onupdate=datetime.utcnow)

    roles = db.relationship("Role", secondary=user_role_assoc, backref="users")

    dateformat = db.Column(db.String(25), default="LLL")
    editor_height = db.Column(db.Integer, default=500)
    use_direct_links = db.Column(db.Boolean, default=True)
    use_embedded_images = db.Column(db.Boolean, default=True)
    markdown_phb_style = db.Column(db.Boolean, default=False)
    quicklinks = db.Column(db.Text)

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

    # TODO: could be more efficient with a query
    def has_char_in_party(self, party):
        for char in self.characters:
            if char in party.members:
                return True

        return False

    # TODO: could be more efficient with a query
    def has_char_in_session(self, session):
        for char in self.characters:
            if session in char.sessions:
                return True

        return False

    def is_dm_of(self, campaign):
        return campaign.dm.id == self.id

    def is_dm_of_anything(self):
        return len(self.campaigns) > 0

    def __repr__(self):
        return '<User {}>'.format(self.username)

    #####
    # LinkGenerator functions
    #####
    def view_text(self):
        return self.username

    def view_url(self):
        return url_for('user.profile', username=self.username)

    def edit_url(self):
        return url_for('user.edit', username=self.username)