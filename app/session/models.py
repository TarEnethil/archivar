from app import db
from app.helpers import urlfriendly
from app.mixins import LinkGenerator, SimpleChangeTracker
from flask import url_for
from sqlalchemy import and_

session_character_assoc = db.Table("session_character_assoc",
                    db.Column("session_id", db.Integer, db.ForeignKey("sessions.id")),
                    db.Column("character_id", db.Integer, db.ForeignKey("characters.id")))

class Session(db.Model, SimpleChangeTracker, LinkGenerator):
    __tablename__ = "sessions"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    summary = db.Column(db.Text)
    dm_notes = db.Column(db.Text)
    date = db.Column(db.DateTime)
    participants = db.relationship("Character", secondary=session_character_assoc, backref="sessions")
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaigns.id"))
    campaign = db.relationship("Campaign", backref="sessions")
    session_number = db.Column(db.Integer)

    #####
    # LinkGenerator functions
    #####
    def view_text(self):
        return "#{} {}".format(self.session_number, self.title)

    def view_url(self):
        return url_for('session.view', id=self.id, name=urlfriendly(self.title))

    def edit_url(self):
        return url_for('session.edit', id=self.id, name=urlfriendly(self.title))

    def delete_url(self):
        return url_for('session.delete', id=self.id, name=urlfriendly(self.title))