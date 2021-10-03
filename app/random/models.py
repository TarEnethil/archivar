from app import db
from app.helpers import urlfriendly
from app.mixins import SimpleChangeTracker, LinkGenerator, PermissionTemplate, Rollable
from d20 import roll as d20roll
from flask import url_for
from flask_login import current_user
from random import choices


class DiceSet(db.Model, Rollable, SimpleChangeTracker, LinkGenerator, PermissionTemplate):
    __tablename__ = "dice_set"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    dice_string = db.Column(db.String(100))

    def roll_once(self):
        return self.roll(1)[0]

    def roll(self, num_rolls):
        return [d20roll(self.dice_string) for i in range(0, num_rolls)]

    def roll_url(self, num_rolls=1):
        if num_rolls == 1:
            return url_for('random.dice_roll', id=self.id, name=urlfriendly(self.name))

        return url_for('random.dice_roll', id=self.id, name=urlfriendly(self.name), num_rolls=num_rolls)

    #####
    # PermissionTemplate functions
    #####
    def is_deletable_by_user(self):
        return self.is_owned_by_user() or current_user.is_at_least_moderator()

    #####
    # LinkGenerator functions
    #####
    def view_text(self):
        return self.name

    def view_url(self):
        return url_for('random.dice_view', id=self.id, name=urlfriendly(self.name))

    def edit_url(self):
        return url_for('random.dice_edit', id=self.id, name=urlfriendly(self.name))

    def delete_url(self):
        return url_for('random.dice_delete', id=self.id, name=urlfriendly(self.name))


class RandomTable(db.Model, Rollable, SimpleChangeTracker, LinkGenerator, PermissionTemplate):
    __tablename__ = "random_table"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    description = db.Column(db.Text)

    def roll_once(self):
        if len(self.entries) == 0:
            return None

        return self.roll(1)[0]

    def roll(self, num_rolls):
        if len(self.entries) == 0:
            return None

        weights = [entry.weight for entry in self.entries]
        return choices(self.entries, weights=weights, k=num_rolls)

    def get_total_weight(self):
        return sum(entry.weight for entry in self.entries)

    def roll_url(self, num_rolls=1):
        if num_rolls == 1:
            return url_for('random.table_roll', id=self.id, name=urlfriendly(self.name))

        return url_for('random.table_roll', id=self.id, name=urlfriendly(self.name), num_rolls=num_rolls)

    #####
    # PermissionTemplate functions
    #####
    def is_deletable_by_user(self):
        return self.is_owned_by_user() or current_user.is_at_least_moderator()

    #####
    # LinkGenerator functions
    #####
    def view_text(self):
        return self.name

    def view_url(self):
        return url_for('random.table_view', id=self.id, name=urlfriendly(self.name))

    def edit_url(self):
        return url_for('random.table_edit', id=self.id, name=urlfriendly(self.name))

    def delete_url(self):
        return url_for('random.table_delete', id=self.id, name=urlfriendly(self.name))


class RandomTableEntry(db.Model, SimpleChangeTracker, LinkGenerator):
    __tablename__ = "random_table_entry"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    weight = db.Column(db.Integer)

    table_id = db.Column(db.Integer, db.ForeignKey('random_table.id'))
    table = db.relationship("RandomTable", backref="entries", foreign_keys=[table_id])

    def get_chance(self):
        return f"{(100.0 * self.weight / self.table.get_total_weight()):0.2f}%"

    #####
    # PermissionTemplate functions
    #####
    def is_deletable_by_user(self):
        return self.is_owned_by_user() or self.table.is_owned_by_user() or current_user.is_at_least_moderator()

    #####
    # LinkGenerator functions
    #####
    def view_text(self):
        return self.title

    def view_url(self):
        return url_for('random.table_entry_view', t_id=self.table_id, t_name=urlfriendly(self.table.name),
                       e_id=self.id, e_name=urlfriendly(self.title))

    def edit_url(self):
        return url_for('random.table_entry_edit', t_id=self.table_id, t_name=urlfriendly(self.table.name),
                       e_id=self.id, e_name=urlfriendly(self.title))

    def delete_url(self):
        return url_for('random.table_entry_delete', t_id=self.table_id, t_name=urlfriendly(self.table.name),
                       e_id=self.id, e_name=urlfriendly(self.title))
