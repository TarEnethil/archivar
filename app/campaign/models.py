from app import db
from app.helpers import urlfriendly
from app.mixins import LinkGenerator, SimpleChangeTracker
from flask import url_for
from jinja2 import Markup

campaign_character_assoc = db.Table("campaign_character_assoc",
                    db.Column("campaign_id", db.Integer, db.ForeignKey("campaigns.id")),
                    db.Column("character_id", db.Integer, db.ForeignKey("characters.id")))

class Campaign(db.Model, SimpleChangeTracker, LinkGenerator):
    __tablename__ = "campaigns"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    color = db.Column(db.String(10))

    dm_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    dm = db.relationship("User", backref="campaigns", foreign_keys=[dm_id])
    dm_notes = db.Column(db.Text)

    default_participants = db.relationship("Character", secondary=campaign_character_assoc, backref="default_participants")

    #####
    # LinkGenerator functions
    #####
    def view_text(self):
        return Markup('<span style="color:{};">█</span> {}'.format(self.color, self.name))

    def view_url(self):
        return url_for('campaign.view', id=self.id, name=urlfriendly(self.name))

    def edit_url(self):
        return url_for('campaign.edit', id=self.id, name=urlfriendly(self.name))