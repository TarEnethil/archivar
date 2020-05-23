from app import db, login
from app.helpers import Role
from app.mixins import LinkGenerator
from datetime import datetime
from flask import url_for, current_app
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

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

    role = db.Column(db.Integer, default=0)

    dateformat = db.Column(db.String(25), default="LLL")
    editor_height = db.Column(db.Integer, default=500)
    use_direct_links = db.Column(db.Boolean, default=True)
    use_embedded_images = db.Column(db.Boolean, default=True)
    markdown_phb_style = db.Column(db.Boolean, default=False)
    quicklinks = db.Column(db.Text)

    def is_admin(self):
        return self.role == Role.Admin.value

    def is_moderator(self):
        return self.role == Role.Moderator.value

    def is_user(self):
        return self.role == Role.User.value

    def is_at_least_moderator(self):
        return self.is_moderator() or self.is_admin()

    def role_name(self):
        return Role(self.role).name

    def has_admin_role(self):
        return self.is_admin()

    def has_map_role(self):
        return self.is_at_least_moderator()

    def has_wiki_role(self):
        return self.is_at_least_moderator()

    def has_special_role(self):
        return self.is_at_least_moderator()

    def is_map_admin(self):
        return self.has_admin_role() or self.has_map_role()

    def is_wiki_admin(self):
        return self.has_admin_role() or self.has_wiki_role()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_characters(self):
        if current_user.id == self.id:
            return self.characters
        else:
            return list(filter(lambda x: x.is_visible, self.characters))

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