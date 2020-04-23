from app import db
from app.helpers import urlfriendly, icon as icon_fkt
from datetime import datetime
from flask import current_app
from flask_login import current_user
from jinja2 import Markup, Template, contextfunction
from sqlalchemy.ext.declarative import declared_attr

def current_user_id():
    try:
        return current_user.id
    except:
        None

class SimpleAuditMixin(object):
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