from app import db
from app.helpers import urlfriendly
from app.mixins import LinkGenerator, SimpleChangeTracker, PermissionTemplate, ProfilePicture
from flask import url_for
from flask_login import current_user
from jinja2 import Markup
from jinja2 import contextfunction

campaign_character_assoc = db.Table("campaign_character_assoc",
                                    db.Column("campaign_id", db.Integer, db.ForeignKey("campaigns.id")),
                                    db.Column("character_id", db.Integer, db.ForeignKey("characters.id")))

campaign_party_assoc = db.Table("campaign_party_assoc",
                                db.Column("campaign_id", db.Integer, db.ForeignKey("campaigns.id")),
                                db.Column("party_id", db.Integer, db.ForeignKey("parties.id")))


class Campaign(db.Model, SimpleChangeTracker, LinkGenerator, PermissionTemplate, ProfilePicture):
    __tablename__ = "campaigns"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    color = db.Column(db.String(10))

    dm_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    dm = db.relationship("User", backref="campaigns", foreign_keys=[dm_id])
    dm_notes = db.Column(db.Text)

    default_participants = db.relationship("Character", secondary=campaign_character_assoc,
                                           backref="default_participants")
    associated_parties = db.relationship("Party", secondary=campaign_party_assoc, backref="associated_campaigns")

    #####
    # Permissions
    #####
    def is_editable_by_user(self):
        return current_user.is_dm_of(self) or current_user.is_admin()

    #####
    # LinkGenerator functions
    #####
    def view_text(self):
        return Markup(f'<span style="color:{self.color};">█</span> {self.name}')

    def view_url(self):
        return url_for('campaign.view', id=self.id, name=urlfriendly(self.name))

    def edit_url(self):
        return url_for('campaign.edit', id=self.id, name=urlfriendly(self.name))

    #####
    # ProfilePicture functions
    #####
    @contextfunction
    def infobox(self, context):
        body = f'<a href="{self.view_url()}" class="stretched-link">{ self.view_text() }</a> \
                 <span class="text-muted d-block">DM: { self.dm.username } | Sessions: { len(self.sessions) }</span>'

        return self.infobox_(context, body)
