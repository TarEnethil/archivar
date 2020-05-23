from app import db
from app.helpers import urlfriendly, link as link_fkt, button as button_fkt, button_nav as button_nav_fkt
from datetime import datetime
from flask import current_app
from flask_login import current_user
from jinja2 import Markup, Template, contextfunction
from sqlalchemy import or_
from sqlalchemy.ext.declarative import declared_attr

def current_user_id():
    try:
        return current_user.id
    except:
        None

class SimpleChangeTracker(object):
    created = db.Column(db.DateTime, default=datetime.utcnow)
    edited = db.Column(db.DateTime, default=None, onupdate=datetime.utcnow)

    @declared_attr
    def created_by_id(cls):
        return db.Column(db.Integer, db.ForeignKey("users.id"), default=current_user_id)

    @declared_attr
    def created_by(cls):
        from app.user.models import User
        return db.relationship(User, primaryjoin=lambda: User.id == cls.created_by_id, foreign_keys = cls.created_by_id)

    @declared_attr
    def edited_by_id(cls):
        return db.Column(db.Integer, db.ForeignKey("users.id"), default=None, onupdate=current_user_id)

    @declared_attr
    def edited_by(cls):
        from app.user.models import User
        return db.relationship(User, primaryjoin=lambda: User.id == cls.edited_by_id, foreign_keys = cls.edited_by_id)

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

class PermissionTemplate(object):
    def is_viewable_for_user(self):
        raise NotImplementedError

    def is_editable_by_user(self):
        raise NotImplementedError

    def is_deletable_by_user(self):
        raise NotImplementedError

class SimplePermissionChecker(PermissionTemplate, SimpleChangeTracker):
    is_visible = db.Column(db.Boolean, default=True)

    @declared_attr
    def is_visible(cls):
        return db.Column(db.Boolean, default=True)

    def is_owned_by_user(self):
        return self.created_by_id == current_user.id

    def is_hideable_by_user(self):
        return self.is_owned_by_user()

    @classmethod
    def get_query_for_visible_items(cls):
        return cls.query.filter(or_(cls.is_visible == True, cls.created_by_id == current_user.id))

    @classmethod
    def get_visible_items(cls):
        return cls.get_query_for_visible_items().all()

class LinkGenerator(object):
    def link(self, url, text, classes=None, ids=None):
        return link_fkt(url, text, classes, ids)

    def button(self, url, text, icon=None, classes=None, ids=None, swap=False, icon_text_class=""):
        return button_fkt(url, text, icon, classes, ids, swap, icon_text_class)

    def view_link(self, text=None, classes=None, ids=None):
        if text == None:
            text = self.view_text()

        return self.link(self.view_url(), text, classes, ids)

    def edit_link(self, text="Edit", classes=None, ids=None):
        if text == None:
            text = self.edit_text()

        return self.link(self.edit_url(), text, classes, ids)

    def delete_link(self, text="Delete", classes=None, ids=None):
        if text == None:
            text = self.delete_text()

        return self.link(self.delete_url(), text, classes, ids)

    def view_button(self, text="View", icon="eye", classes="btn-secondary", ids=None, swap=False):
        return self.button(self.view_url(), text, icon, classes, ids, swap)

    def edit_button(self, text="Edit", icon="edit", classes="btn-secondary", ids=None, swap=False):
        return self.button(self.edit_url(), text, icon, classes, ids, swap)

    def delete_button(self, text="Delete", icon="trash-alt", classes="btn-danger", ids="delete-link", swap=False):
        return self.button(self.delete_url(), text, icon, classes, ids, swap, icon_text_class="text-light")

    def view_button_nav(self, text="View", icon="eye", classes="nav-link", ids=None, swap=False):
        return button_nav_fkt(self.view_url(), text, icon, classes, ids, swap)

    def edit_button_nav(self, text="Edit", icon="edit", classes="nav-link", ids=None, swap=False):
        return button_nav_fkt(self.edit_url(), text, icon, classes, ids, swap)

    def delete_button_nav(self, text="Delete", icon="trash-alt", classes="nav-link bg-danger text-light", ids="delete-link", swap=False):
        return button_nav_fkt(self.delete_url(), text, icon, classes, ids, swap, icon_text_class="text-light", li_classes="ml-auto")

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