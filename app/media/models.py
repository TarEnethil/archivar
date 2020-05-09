from app import db
from app.helpers import urlfriendly
from app.mixins import LinkGenerator, SimpleChangeTracker
from flask import url_for, current_app

class MediaSetting(db.Model, SimpleChangeTracker):
    __tablename__ = "media_settings"
    id = db.Column(db.Integer, primary_key=True)
    default_visible = db.Column(db.Boolean)

class MediaCategory(db.Model, SimpleChangeTracker, LinkGenerator):
    __tablename__ = "media_categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def sidebar_info(self):
        return {
            "id" : self.id,
            "name" : self.name,
            "url" : url_for('media.sidebar', c_id=self.id)
        }

        return dic

    #####
    # LinkGenerator functions
    #####
    def view_text(self):
        return self.name

    def view_url(self):
        return url_for('media.list_by_cat', c_id=self.id, c_name=urlfriendly(self.name))

    def edit_url(self):
        return url_for('media.category_edit', id=self.id, name=urlfriendly(self.name))

class MediaItem(db.Model, SimpleChangeTracker, LinkGenerator):
    __tablename__ = "media"
    id = db.Column(db.Integer, primary_key=True)
    is_visible = db.Column(db.Boolean)
    name = db.Column(db.String(100))
    filename = db.Column(db.String(100))
    filesize = db.Column(db.Integer)
    category_id = db.Column(db.Integer, db.ForeignKey("media_categories.id"))
    category = db.relationship("MediaCategory", backref="items")

    def get_file_ext(self):
        return (self.filename.split(".")[-1]).lower()

    def is_image(self):
        return self.get_file_ext() in current_app.config["MAPNODES_FILE_EXT"]

    def sidebar_info(self):
        return {
            'name' : self.name,
            'filename' : self.filename,
            'view-url' : self.view_url(),
            'serve-url' : self.serve_url(),
            'thumbnail-url' : self.thumbnail_url(),
            'is-image' : self.is_image(),
            "is-visible": self.is_visible
        }


    #####
    # LinkGenerator functions
    #####
    def view_text(self):
        return self.name

    def view_url(self):
        return url_for('media.view', id=self.id, name=urlfriendly(self.name))

    def edit_url(self):
        return url_for('media.edit', id=self.id, name=urlfriendly(self.name))

    def delete_url(self):
        return url_for('media.delete', id=self.id, name=urlfriendly(self.name))

    def serve_url(self):
        return url_for('media.serve_file', filename=self.filename)

    def thumbnail_url(self):
        return url_for('media.serve_thumbnail', filename=self.filename)

    def serve_link(self):
        return self.link(self.serve_url(), self.filename)