from app import db
from app.helpers import urlfriendly
from app.mixins import LinkGenerator, SimpleChangeTracker
from flask import url_for

character_party_assoc = db.Table("character_party_assoc",
                    db.Column("character_id", db.Integer, db.ForeignKey("characters.id")),
                    db.Column("party_id", db.Integer, db.ForeignKey("parties.id")))

class Character(db.Model, SimpleChangeTracker, LinkGenerator):
    __tablename__ = "characters"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    player = db.relationship("User", backref="characters", foreign_keys=[user_id])

    parties = db.relationship("Party", secondary=character_party_assoc, backref="members")

    name = db.Column(db.String(250))
    race = db.Column(db.String(100))
    class_ = db.Column(db.String(100))
    description = db.Column(db.Text)
    dm_notes = db.Column(db.Text)
    private_notes = db.Column(db.Text)

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

class Journal(db.Model, SimpleChangeTracker, LinkGenerator):
    __tablename__ = "journal"

    id = db.Column(db.Integer, primary_key=True)
    is_visible = db.Column(db.Boolean)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)

    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'))
    character = db.relationship("Character", backref="journals", foreign_keys=[character_id])

    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))
    session = db.relationship("Session", backref="journals", foreign_keys=[session_id])

    # LinkGenerator functions
    #####
    def view_text(self):
        return self.title

    def view_url(self):
        return url_for('character.journal_view', c_id=self.character.id, c_name=urlfriendly(self.character.name), j_id=self.id, j_name=urlfriendly(self.title))

    def edit_url(self):
        return url_for('character.journal_edit', c_id=self.character.id, c_name=urlfriendly(self.character.name), j_id=self.id, j_name=urlfriendly(self.title))

    def delete_url(self):
        return url_for('character.journal_delete', c_id=self.character.id, c_name=urlfriendly(self.character.name), j_id=self.id, j_name=urlfriendly(self.title))
