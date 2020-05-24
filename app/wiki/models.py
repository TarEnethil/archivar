from app import db
from app.helpers import urlfriendly
from app.mixins import LinkGenerator, SimpleChangeTracker, SimplePermissionChecker
from flask import url_for
from flask_login import current_user

class WikiSetting(db.Model, SimpleChangeTracker):
    __tablename__ = "wiki_settings"
    id = db.Column(db.Integer, primary_key=True)

class WikiEntry(db.Model, SimplePermissionChecker, LinkGenerator):
    __tablename__ = "wiki_entries"
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(255))
    category = db.Column(db.String(100))
    content = db.Column(db.Text)
    tags = db.Column(db.String(255))

    def split_tags(self):
        return self.tags.split(" ")

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
        return self.title

    def view_url(self):
        return url_for('wiki.view', id=self.id, name=urlfriendly(self.title))

    def edit_url(self):
        return url_for('wiki.edit', id=self.id, name=urlfriendly(self.title))

    def delete_url(self):
        return url_for('wiki.delete', id=self.id, name=urlfriendly(self.title))
