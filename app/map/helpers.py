from app import db
from app.map.models import Map, MapNodeType, MapNode
from app.user.models import User
from datetime import datetime
from flask import flash, redirect, url_for, current_app
from flask_login import current_user
from functools import wraps
from os import path
from sqlalchemy import and_, not_, or_
from werkzeug import secure_filename

# @map_admin_required decorater, use AFTER login_required
def map_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_map_admin():
            flash("You need to be a map admin to perform this action.", "danger")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated_function

# find the best available file name for a map node type image
def map_node_filename(filename_from_form):
    orig_filename = secure_filename(filename_from_form)
    filename = orig_filename

    counter = 1
    while path.isfile(path.join(current_app.config["MAPNODES_DIR"], filename)):
        # fancy duplication avoidance (tm)
        filename = "{}-{}".format(counter, orig_filename)
        counter += 1

    return filename

# generate choices for the node type SelectField
def gen_node_type_choices():
    choices = [(0, "choose...")]

    node_types = MapNodeType.query.all()

    for node_type in node_types:
        choices.append((node_type.id, node_type.name))

    return choices

# generate choices for the submap field
def gen_submap_choices(zerochoice="*no submap*"):
    choices = [(0, zerochoice)]

    maps = Map.query.all()

    for map_ in maps:
        if map_.is_visible:
            choices.append((map_.id, map_.name))
        else:
            choices.append((map_.id, "(invisible) {0}".format(map_.name)))

    return choices

# get all nodes that are visible for the current user
def get_visible_nodes(map_id):
    if current_user.has_admin_role():
        nodes = MapNode.query
    else:
        nodes = MapNode.query.filter(or_(MapNode.is_visible == True, MapNode.created_by_id == current_user.id))

    return nodes.filter_by(on_map=map_id).all()

# get all nodes that are associated with the specified wiki article
def get_nodes_by_wiki_id(w_id):
    if current_user.has_admin_role():
        nodes = MapNode.query
    else:
        nodes = MapNode.query.filter(or_(MapNode.is_visible == True, MapNode.created_by_id == current_user.id))

    nodes = nodes.filter_by(wiki_entry_id = w_id).all()

    return nodes

# set the last update time for a map
def map_changed(id):
    m = Map.query.get(id)

    if m != None:
        m.last_change = datetime.utcnow()

        db.session.commit()
