from flask import render_template, flash, redirect, url_for, request, jsonify, send_from_directory
from app import app, db
from app.map import bp
from app.helpers import page_title, redirect_non_admins, redirect_non_map_admins, flash_no_permission, map_node_filename, gen_node_type_choices
from app.map.forms import MapNodeTypeCreateForm, MapNodeTypeEditForm, MapSettingsForm, MapNodeCreateForm, MapNodeCreateFormAdmin, MapNodeEditForm, MapNodeEditFormAdmin
from app.models import User, Role, GeneralSetting, MapNodeType, MapSetting, MapNode
from flask_login import current_user, login_required
from werkzeug import secure_filename
from datetime import datetime
from PIL import Image
from sqlalchemy import or_, not_, and_
import os

@bp.route("/")
@login_required
def index():
    settings = GeneralSetting.query.get(1)
    mapsettings = MapSetting.query.get(1)

    if settings.world_name:
        title = "Map of " + settings.world_name
    else:
        title = "Worldmap"

    return render_template("map/index.html", settings=mapsettings, title=page_title(title))

@bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    deny_access = redirect_non_map_admins()
    if deny_access:
        return redirect(url_for('index'))

    form = MapSettingsForm()

    settings = MapSetting.query.get(1)

    if form.validate_on_submit():
        settings.min_zoom = form.min_zoom.data
        settings.max_zoom = form.max_zoom.data
        settings.default_zoom = form.default_zoom.data
        settings.icon_anchor = form.icon_anchor.data
        settings.external_provider = form.external_provider.data
        settings.tiles_path = form.tiles_path.data

        db.session.commit()

        flash("Map settings have been changed.", "success")
    elif request.method == "GET":
        form.min_zoom.data = settings.min_zoom
        form.max_zoom.data = settings.max_zoom
        form.default_zoom.data = settings.default_zoom
        form.icon_anchor.data = settings.icon_anchor
        form.external_provider.data = settings.external_provider
        form.tiles_path.data = settings.tiles_path

    node_types = MapNodeType.query.all()

    return render_template("map/settings.html", form=form, node_types=node_types, title=page_title("Map settings"))

@bp.route("/node/create/<x>/<y>", methods=["GET", "POST"])
@login_required
def node_create(x, y):
    if current_user.is_map_admin():
        form = MapNodeCreateFormAdmin()
    else:
        form = MapNodeCreateForm()

    form.coord_x.data = x
    form.coord_y.data = y

    form.node_type.choices = gen_node_type_choices()

    if form.validate_on_submit():
        new_node = MapNode(name=form.name.data, description=form.description.data, node_type=form.node_type.data, coord_x=form.coord_x.data, coord_y=form.coord_y.data, created_by=current_user)

        if current_user.is_map_admin():
            new_node.is_visible = form.is_visible.data

            if new_node.is_visible:
                message = "Node was created."
            else:
                message = "Node was created, it is only visible to map admins."
        else:
            message = "Node was created. Until approved, it is only visible to map admins and you."

        db.session.add(new_node)
        db.session.commit()

        return jsonify(data={'success' : True, 'message': message})
    elif request.method == "POST":
        return jsonify(data={'success' : False, 'message': "Form validation error", 'errors': form.errors})

    return render_template("map/node_create.html", form=form, x=x, y=y)

@bp.route("/node/edit/<id>", methods=["GET", "POST"])
@login_required
def node_edit(id):
    if current_user.is_map_admin():
        form = MapNodeEditFormAdmin()
    else:
        form = MapNodeEditForm()

    form.node_type.choices = gen_node_type_choices()

    node = MapNode.query.filter_by(id=id).first_or_404()

    if not current_user.has_admin_role() and current_user.has_map_role() and node.is_visible == False and node.created_by.has_admin_role():
        flash_no_permission()
        return redirect(url_for('index'))

    if not current_user.is_map_admin() and node.is_visible == False and not node.created_by == current_user:
        flash_no_permission()
        redirect(url_for("index"))

    if form.validate_on_submit():
        node.name = form.name.data
        node.description = form.description.data
        node.node_type = form.node_type.data

        node.coord_x = form.coord_x.data
        node.coord_y = form.coord_y.data

        node.edited = datetime.utcnow()
        node.edited_by = current_user

        if current_user.is_map_admin():
            node.is_visible = form.is_visible.data

        db.session.commit()

        return jsonify(data={'success' : True, 'message': "Node was edited."})
    elif request.method == "POST":
        return jsonify(data={'success' : False, 'message': "Form validation error", 'errors': form.errors})

    form.name.data = node.name
    form.description.data = node.description
    form.node_type.data = node.node_type

    form.coord_x.data = node.coord_x
    form.coord_y.data = node.coord_y

    if current_user.is_map_admin():
        form.is_visible.data = node.is_visible

    return render_template("map/node_edit.html", form=form, node=node)

@bp.route("/node/delete/<id>", methods=["POST"])
@login_required
def node_delete(id):
    if not current_user.is_map_admin():
        return jsonify(data={'success': False, 'message': "You dont have the necessary role to do that."})

    node = MapNode.query.get(id)

    if not node:
        return jsonify(data={'success': False, 'message': "No such id to delete."})

    db.session.delete(node)
    db.session.commit()

    return jsonify(data={"success": True, 'message': "Node was deleted."})

@bp.route("/node_type/create", methods=["GET", "POST"])
@login_required
def node_type_create():
    deny_access = redirect_non_map_admins()
    if deny_access:
        return redirect(url_for('index'))

    form = MapNodeTypeCreateForm()

    if form.validate_on_submit():
        filename = map_node_filename(form.icon.data.filename)
        filepath = os.path.join(app.config["MAPNODES_DIR"], filename)
        form.icon.data.save(filepath)

        icon = Image.open(filepath)
        width, height = icon.size

        new_map_node_type = MapNodeType(name=form.name.data, description=form.description.data, icon_file=filename, icon_width=width, icon_height=height)

        db.session.add(new_map_node_type)
        db.session.commit()

        flash('"' + form.name.data + '" was successfully created.', "success")
        return redirect(url_for('map.settings'))

    return render_template("map/node_type_create.html", form=form, title=page_title("Create map node type"))

@bp.route("/node_type/edit/<id>", methods=["GET", "POST"])
@login_required
def node_type_edit(id):
    deny_access = redirect_non_map_admins()
    if deny_access:
        return redirect(url_for('index'))

    form = MapNodeTypeEditForm()
    node = MapNodeType.query.filter_by(id=id).first_or_404()

    if form.validate_on_submit():
        node.name = form.name.data
        node.description = form.description.data

        if form.icon.data:
            new_filename = map_node_filename(form.icon.data.filename)
            filepath = os.path.join(app.config["MAPNODES_DIR"], filename)
            form.icon.data.save(filepath)

            icon = Image.open(filepath)
            width, height = icon.size

            os.remove(os.path.join(app.config["MAPNODES_DIR"], node.icon_file))

            node.icon_file = new_filename
            node.icon_width = width
            node.icon_height = height

        db.session.commit()
        flash('"' + form.name.data + '" was successfully edited.', "success")
        return redirect(url_for('map.settings'))
    elif request.method == "GET":
        form.name.data = node.name
        form.description.data = node.description

    return render_template("map/node_type_edit.html", form=form, node_type=node, title=page_title("Edit map node type"))

@bp.route("/node_type/json")
@login_required
def node_type_json():
    all_types = MapNodeType.query.all()

    all_types_dict = {}

    for node_type in all_types:
        all_types_dict[node_type.id] = node_type.to_dict()

    return jsonify(all_types_dict)

@bp.route("/node/json")
@login_required
def node_json():
    admins = User.query.filter(User.roles.contains(Role.query.get(1)))

    admin_ids = [a.id for a in admins]

    if current_user.has_admin_role():
        nodes = MapNode.query.all()
    elif current_user.is_map_admin():
        nodes = MapNode.query.filter(not_(and_(MapNode.is_visible == False, MapNode.created_by_id.in_(admin_ids))))
    else:
        nodes = MapNode.query.filter(or_(MapNode.is_visible == True, MapNode.created_by_id == current_user.id)).all()

    nodes_dict = {}

    for node in nodes:
        nodes_dict[node.id] = node.to_dict()

    return jsonify(nodes_dict)

@bp.route("/node_type/icon/<filename>")
@login_required
def node_type_icon(filename):
    return send_from_directory(app.config["MAPNODES_DIR"], filename)

@bp.route("/tile/<path:filename>")
@login_required
def tile(filename):
    return send_from_directory(app.config["MAPTILES_DIR"], filename)
