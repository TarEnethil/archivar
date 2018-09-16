from app import app
from flask import flash
from app.models import GeneralSetting, MapNodeType, Character, Party, Session, WikiEntry, User, Role, Epoch, Month, Day
from flask_login import current_user
from werkzeug import secure_filename
from wtforms.validators import ValidationError
from sqlalchemy import and_, or_, not_
from collections import OrderedDict
import os

def flash_no_permission(msg=None):
    if (msg != None):
        flash(msg)
    else:
        flash("No permission for this action.", "danger")

def redirect_non_admins():
    if not current_user.has_admin_role():
        flash_no_permission()
        return True
    return False

def redirect_non_map_admins():
    if not current_user.is_map_admin():
        flash_no_permission()
        return True
    return False

def redirect_non_wiki_admins():
    if not current_user.is_wiki_admin():
        flash_no_permission()
        return True
    return False

def page_title(dynamic_part=None):
    static_part = GeneralSetting.query.get(1).title

    if dynamic_part != None:
        return static_part + " - " + dynamic_part
    else:
        return static_part

def map_node_filename(filename_from_form):
    filename = secure_filename(filename_from_form)

    counter = 1
    while os.path.isfile(os.path.join(app.config["MAPNODES_DIR"], filename)):
        split = filename.rsplit(".", 1)

        # fancy duplication avoidance (tm)
        filename = split[0] + "-" + str(counter) + "." + split[1]
        counter += 1

    return filename

def gen_node_type_choices():
    choices = [(0, "choose...")]

    node_types = MapNodeType.query.all()

    for node_type in node_types:
        choices.append((node_type.id, node_type.name))

    return choices

def gen_party_members_choices():
    choices = []

    characters = Character.query.all()

    for char in characters:
        choices.append((char.id, char.name + " ("+ char.player.username +")"))

    return choices

def gen_participant_choices():
    choices = []

    parties = Party.query.all()

    for party in parties:
        if len(party.members) == 0:
            continue

        p = (party.name, [])

        for member in party.members:
            p[1].append((member.id, member.name))

        choices.append(p)

    no_party_chars = Character.query.filter(Character.parties==None).all()

    if len(no_party_chars) > 0:
        p = ("No party", [])

        for char in no_party_chars:
            p[1].append((char.id, char.name))

        choices.append(p)

    return choices

def gen_wiki_entry_choices():
    if current_user.has_admin_role():
        entries = WikiEntry.query
    elif current_user.has_wiki_role():
        admins = User.query.filter(User.roles.contains(Role.query.get(1)))
        admin_ids = [a.id for a in admins]
        entries = WikiEntry.query.filter(not_(and_(WikiEntry.is_visible == False, WikiEntry.created_by_id.in_(admin_ids))))
    else:
        entries = WikiEntry.query.filter(or_(WikiEntry.is_visible == True, WikiEntry.created_by_id == current_user.id))

    entries = entries.with_entities(WikiEntry.category, WikiEntry.id, WikiEntry.title).order_by(WikiEntry.title.asc()).all()

    cat_dict = {}

    for entry in entries:
        if entry[0] not in cat_dict:
            cat_dict[entry[0]] = []

        cat_dict[entry[0]].append(entry[1:3])

    ordered = OrderedDict(sorted(cat_dict.items(), key=lambda t: t[0]))

    choices = [(0, "*no linked article*")]

    for k in ordered.keys():
        if k != "":
            p = (k, [])
        else:
            p = ("Main category", [])

        for choice in ordered[k]:
            p[1].append((choice[0], choice[1]))

        choices.append(p)

    return choices

def get_session_number(code):
    q = Session.query.filter(Session.code == code)
    return q.count()

def get_previous_session_id(date, code):
    q = Session.query.filter(and_(Session.code == code, Session.date < date)).order_by(Session.date.desc()).first()

    if q:
        return q.id
    else:
        return

def get_next_session_id(date, code):
    q = Session.query.filter(and_(Session.code == code, Session.date > date)).order_by(Session.date.asc()).first()

    if q:
        return q.id
    else:
        return

def get_next_epoch_order():
    q = Epoch.query.order_by(Epoch.order.desc()).limit(1).first()

    if q:
        return q.order + 1
    else:
        return 1

def get_next_month_order():
    q = Month.query.order_by(Month.order.desc()).limit(1).first()

    if q:
        return q.order + 1
    else:
        return 1

def get_next_day_order():
    q = Day.query.order_by(Day.order.desc()).limit(1).first()

    if q:
        return q.order + 1
    else:
        return 1

def prepare_wiki_nav():
    if current_user.has_admin_role():
        entries = WikiEntry.query.filter(WikiEntry.id != 1)
    elif current_user.has_wiki_role():
        admins = User.query.filter(User.roles.contains(Role.query.get(1)))
        admin_ids = [a.id for a in admins]
        entries = WikiEntry.query.filter(WikiEntry.id != 1, not_(and_(WikiEntry.is_visible == False, WikiEntry.created_by_id.in_(admin_ids))))
    else:
        entries = WikiEntry.query.filter(WikiEntry.id != 1, or_(WikiEntry.is_visible == True, WikiEntry.created_by_id == current_user.id))

    entries = entries.with_entities(WikiEntry.category, WikiEntry.id, WikiEntry.title, WikiEntry.is_visible).order_by(WikiEntry.title.asc()).all()

    cat_dict = {}

    for entry in entries:
        if entry[0] not in cat_dict:
            cat_dict[entry[0]] = []

        cat_dict[entry[0]].append(entry[1:4])

    return OrderedDict(sorted(cat_dict.items(), key=lambda t: t[0]))

def search_wiki_text(text):
    if current_user.has_admin_role():
        entries = WikiEntry.query.filter(WikiEntry.content.contains(text))
    elif current_user.has_wiki_role():
        admins = User.query.filter(User.roles.contains(Role.query.get(1)))
        admin_ids = [a.id for a in admins]
        entries = WikiEntry.query.filter(not_(and_(WikiEntry.is_visible == False, WikiEntry.created_by_id.in_(admin_ids))), WikiEntry.content.contains(text))
    else:
        entries = WikiEntry.query.filter(or_(WikiEntry.is_visible == True, WikiEntry.created_by_id == current_user.id), WikiEntry.content.contains(text))

    entries = entries.with_entities(WikiEntry.id, WikiEntry.title, WikiEntry.content).order_by(WikiEntry.edited.desc())

    return entries.all()

def get_search_context(term, entry_text):
    pos = entry_text.find(term)

    if pos == -1:
        return "ERROR, SHOULD NOT HAPPEN"

    left = max(0, pos - 25)
    right = min(pos + 25, len(entry_text))

    return entry_text[left:right]

def prepare_search_result(term, entries):
    results = []

    for entry in entries:
        if term in entry[2]:
            results.append((entry[0], entry[1], get_search_context(term, entry[2])))

    return results

def search_wiki_tag(tag):
    if current_user.has_admin_role():
        entries = WikiEntry.query.filter(WikiEntry.tags.contains(tag))
    elif current_user.has_wiki_role():
        admins = User.query.filter(User.roles.contains(Role.query.get(1)))
        admin_ids = [a.id for a in admins]
        entries = WikiEntry.query.filter(not_(and_(WikiEntry.is_visible == False, WikiEntry.created_by_id.in_(admin_ids))), WikiEntry.tags.contains(tag))
    else:
        entries = WikiEntry.query.filter(or_(WikiEntry.is_visible == True, WikiEntry.created_by_id == current_user.id), WikiEntry.tags.contains(tag))

    entries = entries.with_entities(WikiEntry.id, WikiEntry.title).order_by(WikiEntry.edited.desc()).all()

    return entries

def get_recently_created():
    if current_user.has_admin_role():
        entries = WikiEntry.query
    elif current_user.has_wiki_role():
        admins = User.query.filter(User.roles.contains(Role.query.get(1)))
        admin_ids = [a.id for a in admins]
        entries = WikiEntry.query.filter(not_(and_(WikiEntry.is_visible == False, WikiEntry.created_by_id.in_(admin_ids))))
    else:
        entries = WikiEntry.query.filter(or_(WikiEntry.is_visible == True, WikiEntry.created_by_id == current_user.id))

    entries = entries.join(User, WikiEntry.created_by_id == User.id).with_entities(WikiEntry.id, WikiEntry.title, WikiEntry.created, User.username).order_by(WikiEntry.created.desc()).limit(5).all()

    return entries

def get_recently_edited():
    if current_user.has_admin_role():
        entries = WikiEntry.query
    elif current_user.has_wiki_role():
        admins = User.query.filter(User.roles.contains(Role.query.get(1)))
        admin_ids = [a.id for a in admins]
        entries = WikiEntry.query.filter(not_(and_(WikiEntry.is_visible == False, WikiEntry.created_by_id.in_(admin_ids))))
    else:
        entries = WikiEntry.query.filter(or_(WikiEntry.is_visible == True, WikiEntry.created_by_id == current_user.id))

    entries = entries.join(User, WikiEntry.edited_by_id == User.id).with_entities(WikiEntry.id, WikiEntry.title, WikiEntry.edited, User.username).order_by(WikiEntry.edited.desc()).limit(5).all()

    return entries

class XYZ_Validator(object):
    def __call__(self, form, field):
        if not "{x}" in field.data or not "{y}" in field.data or not "{z}" in field.data:
            raise ValidationError("The tile provider needs the arguments {x} {y} and {z}")

class LessThanOrEqual(object):
    def __init__(self, comp_value_field_name):
        self.comp_value_field_name = comp_value_field_name

    def __call__(self, form, field):
        other_field = form._fields.get(self.comp_value_field_name)

        if other_field is None:
            raise Exception('No field named %s in form' % self.comp_value_field_name)

        if other_field.data and field.data:
            if field.data > other_field.data:
                raise ValidationError("Value must be less than or equal to %s" % self.comp_value_field_name)

class GreaterThanOrEqual(object):
    def __init__(self, comp_value_field_name):
        self.comp_value_field_name = comp_value_field_name

    def __call__(self, form, field):
        other_field = form._fields.get(self.comp_value_field_name)

        if other_field is None:
            raise Exception('No field named %s in form' % self.comp_value_field_name)

        if other_field.data and field.data:
            if field.data < other_field.data:
                raise ValidationError("Value must be greater than or equal to %s" % self.comp_value_field_name)