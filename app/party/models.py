from app import db
from app.helpers import urlfriendly
from app.mixins import LinkGenerator, SimpleChangeTracker, PermissionTemplate, ProfilePicture
from flask import url_for
from flask_login import current_user
from jinja2 import pass_context


class Party(db.Model, SimpleChangeTracker, LinkGenerator, PermissionTemplate, ProfilePicture):
    __tablename__ = "parties"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)

    #####
    # Permissions
    #####
    def is_editable_by_user(self):
        return current_user.is_admin() or \
               current_user.has_char_in_party(self) or \
               current_user.is_assoc_dm_of_party(self)

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

    #####
    # ProfilePicture functions
    #####
    @pass_context
    def infobox(self, context):
        body = f'<a href="{self.view_url()}" class="stretched-link">{ self.name }</a> \
                 <span class="text-muted d-block">Members: { len(self.members) }</span>'

        return self.infobox_(context, body)
