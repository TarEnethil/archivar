from app.user.models import User
from app.wiki.models import WikiEntry
from collections import OrderedDict
from flask import redirect, flash, url_for
from flask_login import current_user
from functools import wraps
from sqlalchemy import and_, or_, not_

# generate choices for the wiki link SelectField for map nodes
def gen_wiki_entry_choices(ensure=None):
    # get visible wiki entries for current user
    entries = WikiEntry.query.order_by(WikiEntry.title.asc()).all()

    cat_dict = {}

    # make dict by wiki category
    for entry in entries:
        if entry.is_viewable_by_user() or (ensure != None and ensure == entry):
            cat = entry.category
            if cat not in cat_dict:
                cat_dict[cat] = []

            name = entry.title

            if entry.is_visible == False:
                name = "{} (invisible)".format(name)
            cat_dict[cat].append([entry.id, name])

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

    entries = WikiEntry.get_query_for_visible_items(include_hidden_for_user=True)
    categories = entries.with_entities(WikiEntry.category).distinct()

    for cat in categories:
        if cat[0] != "":
            choices.append((cat[0], cat[0]))

    return choices

# generate data for the wiki navigation
def prepare_wiki_nav():
    # get all visible wiki entries for current user
    entries = WikiEntry.get_query_for_visible_items(include_hidden_for_user=True)
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
    entries = WikiEntry.query.filter(or_(WikiEntry.is_visible == True, WikiEntry.created_by_id == current_user.id), WikiEntry.tags.contains(tag))
    entries = entries.with_entities(WikiEntry.id, WikiEntry.title).order_by(WikiEntry.edited.desc()).all()

    return entries

# get the last 5 created articles that are visible for the user
def get_recently_created():
    entries = WikiEntry.get_query_for_visible_items(include_hidden_for_user=True)
    entries = entries.join(User, WikiEntry.created_by_id == User.id).with_entities(WikiEntry.id, WikiEntry.title, WikiEntry.created, User.username).order_by(WikiEntry.created.desc()).limit(5).all()

    return entries

# get the last 5 edited articles that are visible for the user
def get_recently_edited():
    entries = WikiEntry.get_query_for_visible_items(include_hidden_for_user=True)
    entries = entries.join(User, WikiEntry.edited_by_id == User.id).with_entities(WikiEntry.id, WikiEntry.title, WikiEntry.edited, User.username).order_by(WikiEntry.edited.desc()).limit(5).all()

    return entries

# generate list of categories (excluding '')
def gen_category_strings():
    entries = WikiEntry.get_query_for_visible_items(include_hidden_for_user=True)
    entries = entries.with_entities(WikiEntry.category).distinct().all()

    cats = []

    for cat in entries:
        if cat[0] != '':
            cats.append(cat[0])

    return cats