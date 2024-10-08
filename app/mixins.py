from app import db
from app.helpers import link as link_fkt, button as button_fkt, button_nav as button_nav_fkt
from datetime import datetime
from flask import current_app, url_for
from flask_login import current_user
from jinja2 import Template, pass_context
from markupsafe import Markup
from sqlalchemy import or_
from sqlalchemy.ext.declarative import declared_attr


def current_user_id():
    try:
        return current_user.id
    except Exception:
        None


class SimpleChangeTracker(object):
    created = db.Column(db.DateTime, default=datetime.utcnow)
    edited = db.Column(db.DateTime, default=None, onupdate=datetime.utcnow)

    def is_owned_by_user(self):
        return self.created_by_id == current_user.id

    @declared_attr
    def created_by_id(cls):
        return db.Column(db.Integer, db.ForeignKey("users.id"), default=current_user_id)

    @declared_attr
    def created_by(cls):
        from app.user.models import User
        return db.relationship(User, primaryjoin=lambda: User.id == cls.created_by_id, foreign_keys=cls.created_by_id)

    @declared_attr
    def edited_by_id(cls):
        return db.Column(db.Integer, db.ForeignKey("users.id"), default=None, onupdate=current_user_id)

    @declared_attr
    def edited_by(cls):
        from app.user.models import User
        return db.relationship(User, primaryjoin=lambda: User.id == cls.edited_by_id, foreign_keys=cls.edited_by_id)

    @pass_context
    def print_info(self, context, create=True, edit=True, hr=True):
        if current_user.is_authenticated:
            dateformat = current_user.dateformat
        else:
            dateformat = "LLL"

        out = ""

        if hr is True:
            out += '<hr>'

        out += '<ul class="list-unstyled">'

        if create is True and (self.created_by or self.created):
            out += "<li>Created"

            if self.created_by:
                out += f' by {self.created_by.view_link()}'

            if self.created:
                out += f' on {current_app.extensions["moment"](self.created).format(dateformat)}'

            out += "</li>"

        if edit is True and (self.edited_by or self.edited):
            out += "<li>Edited"

            if self.edited_by:
                out += f' by {self.edited_by.view_link()}'

            if self.edited:
                out += f' on {current_app.extensions["moment"](self.edited).format(dateformat)}'

            out += "</li>"

        if "Created" not in out and "Edited" not in out:
            return ""

        return Markup(Template(out).render(context))


class PermissionTemplate(object):
    def is_editable_by_user(self):
        raise NotImplementedError

    def is_deletable_by_user(self):
        raise NotImplementedError


class SimplePermissionChecker(PermissionTemplate, SimpleChangeTracker):
    is_visible = db.Column(db.Boolean, default=True)

    @declared_attr
    def is_visible(cls):  # noqa: F811
        return db.Column(db.Boolean, default=True)

    def is_viewable_by_user(self):
        raise NotImplementedError

    def is_hideable_by_user(self):
        return self.is_owned_by_user()

    @classmethod
    def get_query_for_visible_items(cls, include_hidden_for_user=False):
        """
        is_visible == True works too, but is not PEP-compliant
        is_visible is True does not work correctly
        -> use is_visible.is_(True)
        found via unit testing
        """
        if include_hidden_for_user and current_user.is_authenticated:
            return cls.query.filter(or_(cls.is_visible.is_(True), cls.created_by_id == current_user.id))
        else:
            return cls.query.filter(cls.is_visible.is_(True))

    @classmethod
    def get_visible_items(cls, include_hidden_for_user=False, order_desc=False):
        query = cls.get_query_for_visible_items(include_hidden_for_user)

        if order_desc:
            query = query.order_by(cls.id.desc())

        return query.all()


class LinkGenerator(object):
    def link(self, url, text, classes=None, ids=None):
        return link_fkt(url, text, classes, ids)

    def button(self, url, text, icon=None, classes=None, ids=None, swap=False, icon_text_class=""):
        return button_fkt(url, text, icon, classes, ids, swap, icon_text_class)

    def button_nav(self, url, text, icon=None, classes="nav-link", ids=None, swap=False):
        return button_nav_fkt(url, text, icon, classes, ids, swap)

    def view_link(self, text=None, classes=None, ids=None):
        if text is None:
            text = self.view_text()

        return self.link(self.view_url(), text, classes, ids)

    def edit_link(self, text="Edit", classes=None, ids=None):
        if text is None:
            text = self.edit_text()

        return self.link(self.edit_url(), text, classes, ids)

    def delete_link(self, text="Delete", classes=None, ids=None):
        if text is None:
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

    def delete_button_nav(self, text="Delete", icon="trash-alt", classes="nav-link bg-danger text-light",
                          ids="delete-link", swap=False):
        return button_nav_fkt(self.delete_url(), text, icon, classes, ids, swap, icon_text_class="text-light",
                              li_classes="ms-auto")

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


class ProfilePicture(object):
    profile_picture = db.Column(db.String(100))

    def infobox_(self, context, body):
        out = f'\
        <div class="col-xl-4 col-lg-6 col-md-6 col-sm-12 infobox"> \
            <div class="d-flex position-relative p-3 border m-1 align-items-center"> \
                <div class="flex-shrink-0 infobox-img-container align-self-center"> \
                    <img src="{self.profile_thumbnail_url()}" class="align-self-center"> \
                </div> \
                <div class="flex-grow-1 text-truncate"> \
                    {body} \
                </div> \
            </div> \
        </div>'

        return Markup(Template(out).render(context))

    # needs to be overridden by base class
    def infobox(self):
        raise NotImplementedError

    def profile_picture_url(self):
        if (self.profile_picture):
            return url_for('media.profile_picture', filename=self.profile_picture)
        else:
            return url_for('static', filename="no_profile.png")

    def profile_thumbnail_url(self):
        if (self.profile_picture):
            return url_for('media.profile_picture_thumb', filename=self.profile_picture)
        else:
            return url_for('static', filename="no_profile.png")


class Rollable(object):
    def roll_once(self):
        raise NotImplementedError

    def roll(self, num_rolls):
        raise NotImplementedError

    def roll_url(self, num_rolls=1):
        raise NotImplementedError

    def roll_button(self, text="Roll", icon="dice", classes="btn-secondary", ids=None, swap=False):
        return self.button(self.roll_url(), text, icon, classes, ids, swap)

    def roll_button_nav(self, text="Roll", icon="dice", classes="", ids=None, swap=False):
        return self.button_nav(self.roll_url(), text, icon, classes, ids, swap)
