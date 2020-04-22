from app import db
from app.helpers import urlfriendly
from app.user.models import LinkGenerator, SimpleAuditMixin
from flask import url_for

class Party(db.Model, SimpleAuditMixin, LinkGenerator):
    __tablename__ = "parties"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    dm_notes = db.Column(db.Text)

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