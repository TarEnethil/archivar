from app import db
from app.helpers import urlfriendly
from app.mixins import LinkGenerator, SimplePermissionChecker, ProfilePicture
from flask import url_for
from flask_login import current_user
from jinja2 import contextfunction

character_party_assoc = db.Table("character_party_assoc",
                                 db.Column("character_id", db.Integer, db.ForeignKey("characters.id")),
                                 db.Column("party_id", db.Integer, db.ForeignKey("parties.id")))


class Character(db.Model, SimplePermissionChecker, LinkGenerator, ProfilePicture):
    __tablename__ = "characters"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    player = db.relationship("User", backref="characters", foreign_keys=[user_id])

    parties = db.relationship("Party", secondary=character_party_assoc, backref="members")

    name = db.Column(db.String(250))
    race = db.Column(db.String(100))
    class_ = db.Column(db.String(100))
    description = db.Column(db.Text)
    private_notes = db.Column(db.Text)

    def get_journals(self):
        if self.user_id == current_user.id:
            return self.journals
        else:
            return (list(filter(lambda x: x.is_viewable_by_user(), self.journals)))

    #####
    # Permissions
    #####
    def is_viewable_by_user(self):
        return self.is_visible or self.is_owned_by_user()

    def is_editable_by_user(self):
        return self.is_owned_by_user()

    def is_deletable_by_user(self):
        return self.is_owned_by_user() or (self.is_visible and current_user.is_admin())

    def is_owned_by_user(self):
        return self.user_id == current_user.id

    def journal_is_creatable_by_user(self):
        return self.is_owned_by_user()

    #####
    # LinkGenerator functions
    #####
    def view_text(self):
        return self.name

    def view_url(self):
        return url_for('character.view', id=self.id, name=urlfriendly(self.name))

    def edit_url(self):
        return url_for('character.edit', id=self.id, name=urlfriendly(self.name))

    def delete_url(self):
        return url_for('character.delete', id=self.id, name=urlfriendly(self.name))

    #####
    # ProfilePicture functions
    #####
    @contextfunction
    def infobox(self, context, add_classes=""):
        body = f'<a href="{self.view_url()}" class="stretched-link {add_classes}">{ self.name }</a> \
                 <span class="text-muted d-block">{ self.race } { self.class_ }</span>'

        return self.infobox_(context, body)


class Journal(db.Model, SimplePermissionChecker, LinkGenerator, ProfilePicture):
    __tablename__ = "journal"
    # we just want the functions, not the field
    profile_picture = None

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)

    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'))
    character = db.relationship("Character", backref="journals", foreign_keys=[character_id])

    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))
    session = db.relationship("Session", backref="journals", foreign_keys=[session_id])

    #####
    # Permissions
    #####
    def is_viewable_by_user(self):
        return self.is_visible or self.is_owned_by_user()

    def is_editable_by_user(self):
        return self.is_owned_by_user()

    def is_deletable_by_user(self):
        return self.is_owned_by_user() or (self.is_visible and current_user.is_admin())

    def is_owned_by_user(self):
        return self.character.user_id == current_user.id

    #####
    # LinkGenerator functions
    #####
    def view_text(self):
        return self.title

    def view_url(self):
        return url_for('character.journal_view', c_id=self.character.id, c_name=urlfriendly(self.character.name),
                       j_id=self.id, j_name=urlfriendly(self.title))

    def edit_url(self):
        return url_for('character.journal_edit', c_id=self.character.id, c_name=urlfriendly(self.character.name),
                       j_id=self.id, j_name=urlfriendly(self.title))

    def delete_url(self):
        return url_for('character.journal_delete', c_id=self.character.id, c_name=urlfriendly(self.character.name),
                       j_id=self.id, j_name=urlfriendly(self.title))

    #####
    # ProfilePicture functions
    #####
    @contextfunction
    def infobox(self, context, add_classes=""):
        body = f'<a href="{self.view_url()}" class="stretched-link {add_classes}">{ self.title }</a> \
                 <span class="text-muted d-block">by {self.character.name}</span>'

        return self.infobox_(context, body)

    # return character portrait instead
    def profile_picture_url(self):
        return self.character.profile_picture_url()

    # return character thumbnail instead
    def profile_thumbnail_url(self):
        return self.character.profile_thumbnail_url()
