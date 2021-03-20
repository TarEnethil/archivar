from app import db
from app.helpers import upload_file
from app.map.models import Map, MapNodeType, MapNode
from app.user.models import User
from datetime import datetime
from flask import flash, redirect, url_for, current_app
from flask_login import current_user
from functools import wraps
from os import path, remove
from sqlalchemy import and_, not_, or_
from PIL import Image

def upload_node_icon(filedata, filename=None):
    path_ = current_app.config["MAPNODES_DIR"]
    success, filename = upload_file(filedata, path_, filename)

    if False ==  success:
        return False, filename, 0, 0

    try:
        width, height = Image.open(path.join(path_, filename)).size
    except:
        flash("Error while getting icon size", "error")
        return False, filename, 0, 0

    return True, filename, width, height

def delete_node_icon(filename):
    try:
        remove(path.join(current_app.config["MAPNODES_DIR"], filename))
    except:
        flash(f"Could not delete old icon {filename}", "warning")

# generate choices for the node type SelectField
def gen_node_type_choices():
    choices = [(0, "choose...")]

    node_types = MapNodeType.query.all()

    for node_type in node_types:
        choices.append((node_type.id, node_type.name))

    return choices

# generate choices for the submap field
def gen_submap_choices(zerochoice="*no submap*", ensure=None):
    choices = [(0, zerochoice)]

    maps = Map.query.all()

    for map_ in maps:
        if map_.is_viewable_by_user() or (ensure != None and map_ == ensure):
            name = map_.name

            if map_.is_visible == False:
                name = "{} (invisible)".format(name)

            choices.append((map_.id, name))

    return choices

# get all nodes that are visible for the current user
def get_visible_nodes(map_id):
    nodes = MapNode.get_query_for_visible_items(include_hidden_for_user=True)
    return nodes.filter_by(on_map=map_id).all()

# get all nodes that are associated with the specified wiki article
def get_nodes_by_wiki_id(w_id):
    nodes = MapNode.get_query_for_visible_items(include_hidden_for_user=True)
    nodes = nodes.filter_by(wiki_entry_id = w_id).all()

    return nodes

# set the last update time for a map
def map_changed(id):
    m = Map.query.get(id)

    if m != None:
        m.last_change = datetime.utcnow()

        db.session.commit()
