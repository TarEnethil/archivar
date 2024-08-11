from app import db
from app.helpers import urlfriendly
from app.mixins import LinkGenerator, SimpleChangeTracker, PermissionTemplate, ProfilePicture
from flask import url_for
from flask_login import current_user
from jinja2 import pass_context

session_character_assoc = db.Table("session_character_assoc",
                                   db.Column("session_id", db.Integer, db.ForeignKey("sessions.id")),
                                   db.Column("character_id", db.Integer, db.ForeignKey("characters.id")))


class Session(db.Model, SimpleChangeTracker, LinkGenerator, PermissionTemplate, ProfilePicture):
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

    profile_picture = None  # we only want the infobox functions, not the column

    def anchor_text(self):
        return urlfriendly(f"session-{self.session_number}")

    #####
    # Permissions
    #####
    def is_editable_by_user(self):
        return current_user.is_admin() or current_user.is_dm_of(self.campaign) or current_user.has_char_in_session(self)

    def is_deletable_by_user(self):
        return current_user.is_admin() or current_user.is_dm_of(self.campaign)

    #####
    # LinkGenerator functions
    #####
    def view_text(self):
        return f"#{self.session_number} {self.title}"

    def view_url(self):
        return url_for('session.view', id=self.id, name=urlfriendly(self.title))

    def edit_url(self):
        return url_for('session.edit', id=self.id, name=urlfriendly(self.title))

    def delete_url(self):
        return url_for('session.delete', id=self.id, name=urlfriendly(self.title))

    #####
    # ProfilePicture functions
    #####
    @pass_context
    def infobox(self, context, info=""):
        if current_user.is_dm_of(self.campaign):
            role = "as DM"
        else:
            chars = current_user.get_chars_in_session(self)

            if len(chars) == 1:
                role = f"as {chars[0].name}"
            elif len(chars) > 1:
                role = f"as {len(chars)} characters"
            else:
                role = ""

        body = f'{info} <a href="{self.view_url()}" class="stretched-link"> {self.view_text()}</a> \
                 <span class="text-muted d-block">{role}</span>'

        return self.infobox_(context, body)

    def profile_picture_url(self):
        return self.campaign.profile_picture_url()

    def profile_thumbnail_url(self):
        return self.campaign.profile_thumbnail_url()
