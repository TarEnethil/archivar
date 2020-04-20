from app import db, login
from app.helpers import urlfriendly, icon as icon_fkt
from datetime import datetime
from flask import url_for, current_app
from flask_login import UserMixin, current_user
from jinja2 import Markup, Template, contextfunction
from sqlalchemy.ext.declarative import declared_attr
from werkzeug.security import generate_password_hash, check_password_hash

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

def current_user_id():
    try:
        return current_user.id
    except:
        None

user_role_assoc = db.Table("user_role_assoc",
                            db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
                            db.Column("role_id", db.Integer, db.ForeignKey("roles.id")))

class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    description = db.Column(db.String(256))

class SimpleAuditMixin(object):
    created = db.Column(db.DateTime, default=datetime.utcnow)
    edited = db.Column(db.DateTime, default=None, onupdate=datetime.utcnow)

    @declared_attr
    def created_by_id(cls):
        return db.Column(db.Integer, db.ForeignKey("users.id"), default=current_user_id)

    @declared_attr
    def created_by(cls):
        return db.relationship(User, primaryjoin=lambda: User.id == cls.created_by_id, foreign_keys = cls.created_by_id)

    @declared_attr
    def edited_by_id(cls):
        return db.Column(db.Integer, db.ForeignKey("users.id"), default=None, onupdate=current_user_id)

    @declared_attr
    def edited_by(cls):
        return db.relationship("User", primaryjoin=lambda: User.id == cls.edited_by_id, foreign_keys = cls.edited_by_id)

    @contextfunction
    def print_info(self, context, create=True, edit=True, hr=True):
        out = ""

        if hr == True:
            out += '<hr>'

        out += '<ul class="list-unstyled">'

        if create == True and (self.created_by or self.created):
            out += "<li>Created"

            if self.created_by:
                out += ' by {}'.format(self.created_by.view_link())

            if self.created:
                out += " on {}".format(current_app.extensions["moment"](self.created).format(current_user.dateformat))

            out += "</li>"


        if edit == True and (self.edited_by or self.edited):
            out += "<li>Edited"

            if self.edited_by:
                out += ' by {}'.format(self.edited_by.view_link())

            if self.edited:
                out += " on {}".format(current_app.extensions["moment"](self.edited).format(current_user.dateformat))

            out += "</li>"

        if not "Created" in out and not "Edited" in out:
            return ""

        return Markup(Template(out).render(context))

class LinkGenerator(object):
    def link(self, url, text, classes=None, ids=None):
        attrs = ""

        if classes != None:
            attrs += 'class="{}"'.format(classes)

        if ids != None:
            attrs += 'id="{}"'.format(ids)

        return Markup('<a href="{}" {}>{}</a>'.format(url, attrs, text))

    def button(self, url, text, icon=None, classes=None, ids=None, swap=False):
        if icon != None:
            icon = icon_fkt(icon)

        if swap == False:
            text = "{}\n{}".format(icon, text)
        else:
            text = "{}\n{}".format(text, icon)

        link = self.link(url, text, classes, ids)

        return Markup(link)

    def view_link(self, text=None, classes=None, ids=None):
        if text == None:
            text = self.view_text()

        return self.link(self.view_url(), text, classes, ids)

    def edit_link(self, text="Edit", css_classes=None, css_ids=None):
        if text == None:
            text = self.edit_text()

        return self.link(self.edit_url(), text, classes, ids)

    def delete_link(self, text="Delete", css_classes=None, css_ids=None):
        if text == None:
            text = self.delete_text()

        return self.link(self.delete_url(), text, classes, ids)

    def view_button(self, text="View", icon="eye", classes="btn btn-default", ids=None, swap=False):
        return self.button(self.view_url(), text, icon, classes, ids, swap)

    def edit_button(self, text="Edit", icon="edit", classes="btn btn-default", ids=None, swap=False):
        return self.button(self.edit_url(), text, icon, classes, ids, swap)

    def delete_button(self, text="Delete", icon="trash-alt", classes="btn btn-danger", ids="delete-link", swap=False):
        return self.button(self.delete_url(), text, icon, classes, ids, swap)

    def view_button_nav(self, text="View", icon="eye", classes=None, ids=None, swap=False):
        return self.button(self.view_url(), text, icon, classes, ids, swap)

    def edit_button_nav(self, text="Edit", icon="edit", classes=None, ids=None, swap=False):
        return self.button(self.edit_url(), text, icon, classes, ids, swap)

    def delete_button_nav(self, text="Delete", icon="trash-alt", classes="btn btn-danger", ids="delete-link", swap=False):
        return self.button(self.delete_url(), text, icon, classes, ids, swap)

    def view_text(self):
        return "View"

    def edit_text(self):
        return "Edit"

    def delete_text(self):
        return "Delete"

    # needs to be overridden by base class
    def view_url(self):
        raise NotImplementedError

    # needs to be overridden by base class
    def edit_url(self):
        raise NotImplementedError

    # needs to be overridden by base class
    def delete_url(self):
        raise NotImplementedError

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