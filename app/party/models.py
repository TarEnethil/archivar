from app import db
from app.helpers import urlfriendly
from app.mixins import LinkGenerator, SimpleChangeTracker, PermissionTemplate
from flask import url_for
from flask_login import current_user

class Party(db.Model, SimpleChangeTracker, LinkGenerator, PermissionTemplate):
    __tablename__ = "parties"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)

    #####
    # Permissions
    #####
    def is_editable_by_user(self):
        return current_user.is_admin() or current_user.has_char_in_party(self)

    def is_deletable_by_user(self):
        return current_user.is_admin()

    #####
    # LinkGenerator functions
    #####
    def view_text(self):
        return self.name

    def view_url(self):
        return url_for('party.view', id=self.id, name=urlfriendly(self.name))

    def edit_url(self):
        return url_for('party.edit', id=self.id, name=urlfriendly(self.name))

    def delete_url(self):
        return url_for('party.delete', id=self.id, name=urlfriendly(self.name))