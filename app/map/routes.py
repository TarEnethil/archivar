from flask import render_template, flash, redirect, url_for, request, jsonify, send_from_directory
from app import app, db
from app.map import bp
from app.helpers import page_title, redirect_non_admins, redirect_non_map_admins, map_node_filename, gen_node_type_choices
from app.map.forms import MapNodeTypeCreateForm, MapNodeTypeEditForm, MapSettingsForm, MapNodeCreateForm, MapNodeCreateFormAdmin
from app.models import User, Role, MapNodeType, MapSetting, MapNode
from flask_login import current_user, login_required
from werkzeug import secure_filename
import os

@bp.route("/")
@login_required
def index():
    settings = MapSetting.query.get(1)

    return render_template("map/index.html", settings=settings, title=page_title("Worldmap"))

@bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    redirect_non_map_admins()

    form = MapSettingsForm()

    settings = MapSetting.query.get(1)

    if form.validate_on_submit():
        settings.min_zoom = form.min_zoom.data 
        settings.max_zoom = form.max_zoom.data 
        settings.default_zoom = form.default_zoom.data 

        if form.tiles_path.data.endswith("/") or not form.tiles_path.data:
            settings.tiles_path = form.tiles_path.data
        else:
            settings.tiles_path = form.tiles_path.data + "/"

        db.session.commit()

        flash("Map settings have been changed.")

    form.min_zoom.data = settings.min_zoom
    form.max_zoom.data = settings.max_zoom
    form.default_zoom.data = settings.default_zoom
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

@bp.route("/node_type/create", methods=["GET", "POST"])
@login_required
def node_type_create():
    redirect_non_map_admins()
    
    form = MapNodeTypeCreateForm()

    if form.validate_on_submit():
        filename = map_node_filename(form.icon.data.filename)

        new_map_node_type = MapNodeType(name=form.name.data, description=form.description.data, icon_file=filename)

        db.session.add(new_map_node_type)
        db.session.commit()
        form.icon.data.save(os.path.join(app.config["MAPNODES_DIR"], filename))

        flash('"' + form.name.data + '" was successfully created.')
        return redirect(url_for('map.settings'))
    
    return render_template("map/node_type_create.html", form=form, title=page_title("Create map node type"))

@bp.route("/node_type/edit/<id>", methods=["GET", "POST"])
@login_required
def node_type_edit(id):
    redirect_non_map_admins()

    form = MapNodeTypeEditForm()
    node = MapNodeType.query.filter_by(id=id).first_or_404()

    if form.validate_on_submit():
        node.name = form.name.data
        node.description = form.description.data

        if form.icon.data:
            new_filename = map_node_filename(form.icon.data.filename)
            form.icon.data.save(os.path.join(app.config["MAPNODES_DIR"], new_filename))

            os.remove(os.path.join(app.config["MAPNODES_DIR"], node.icon_file))

            node.icon_file = new_filename

        db.session.commit()
        flash('"' + form.name.data + '" was successfully edited.')
        return redirect(url_for('map.settings'))

    form.name.data = node.name
    form.description.data = node.description
    return render_template("map/node_type_edit.html", form=form, node_type=node, title=page_title("Edit map node type"))

@bp.route("/node_type/icon/<filename>")
@login_required
def node_type_icon(filename):
    return send_from_directory(app.config["MAPNODES_DIR"], filename)

@bp.route("/tile/<path:filename>")
@login_required
def tile(filename):
    return send_from_directory(app.config["MAPTILES_DIR"], filename)
