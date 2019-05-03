from app.models import Role, User, WikiEntry
from flask import redirect, flash, url_for
from functools import wraps
from collections import OrderedDict
from flask_login import current_user
from sqlalchemy import and_, or_, not_

# @wiki_admin_required decorater, use AFTER login_required
def wiki_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_wiki_admin():
            flash("You need to be a wiki admin to perform this action.", "danger")
            return redirect(url_for("wiki.index"))
        return f(*args, **kwargs)
    return decorated_function

# generate choices for the wiki link SelectField for map nodes
def gen_wiki_entry_choices():
    # get visible wiki entries for current user
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

    # make dict by wiki category
    for entry in entries:
        if entry[0] not in cat_dict:
            cat_dict[entry[0]] = []

        cat_dict[entry[0]].append(entry[1:3])

    ordered = OrderedDict(sorted(cat_dict.items(), key=lambda t: t[0]))

    choices = [(0, "*no linked article*")]

    # nested touples by category (optgroup)
    for k in ordered.keys():
        if k != "":
            p = (k, [])
        else:
            p = ("Main category", [])

        for choice in ordered[k]:
            p[1].append((choice[0], choice[1]))

        choices.append(p)

    return choices

# get a list of distinct categories, excluding the empty category
def gen_wiki_category_choices():
    choices = [("", "choose a category")]

    categories = WikiEntry.query.with_entities(WikiEntry.category).distinct()

    for cat in categories:
        if cat[0] != "":
            choices.append((cat[0], cat[0]))


    return choices

# generate data for the wiki navigation
def prepare_wiki_nav():
    # get all visible wiki entries for current user
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

    # nested touples for categories
    for entry in entries:
        if entry[0] not in cat_dict:
            cat_dict[entry[0]] = []

        cat_dict[entry[0]].append(entry[1:4])

    return OrderedDict(sorted(cat_dict.items(), key=lambda t: t[0]))

# get all visible wiki entries for the current user containing the search text
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

# generate a text snipped from the whole text
def get_search_context(term, entry_text):
    pos = entry_text.find(term)

    if pos == -1:
        return "ERROR, SHOULD NOT HAPPEN"

    left = max(0, pos - 25)
    right = min(pos + 25, len(entry_text))

    return entry_text[left:right]

# find context for every search match
def prepare_search_result(term, entries):
    results = []

    for entry in entries:
        if term in entry[2]:
            results.append((entry[0], entry[1], get_search_context(term, entry[2])))

    return results

# search the tags of all visible entries for current user for specified tag
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

# get the last 5 created articles that are visible for the user
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

# get the last 5 edited articles that are visible for the user
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