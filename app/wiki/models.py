from app import db
from app.helpers import urlfriendly
from app.mixins import LinkGenerator, SimpleChangeTracker
from flask import url_for

class WikiSetting(db.Model, SimpleChangeTracker):
    __tablename__ = "wiki_settings"
    id = db.Column(db.Integer, primary_key=True)
    default_visible = db.Column(db.Boolean, default=False)

class WikiEntry(db.Model, SimpleChangeTracker, LinkGenerator):
    __tablename__ = "wiki_entries"
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(255))
    category = db.Column(db.String(100))
    is_visible = db.Column(db.Boolean)
    content = db.Column(db.Text)
    dm_content = db.Column(db.Text)
    tags = db.Column(db.String(255))

    def split_tags(self):
        return self.tags.split(" ")

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
