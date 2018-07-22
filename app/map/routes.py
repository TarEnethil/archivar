from flask import render_template, flash, redirect, url_for, request, jsonify, send_from_directory
from app import app, db
from app.map import bp
from app.helpers import page_title, redirect_non_admins, redirect_non_map_admins, map_node_filename
from app.map.forms import MapNodeTypeCreateForm, MapNodeTypeEditForm
from app.models import User, Role, MapNodeType
from flask_login import current_user, login_required
from werkzeug import secure_filename
import os

@bp.route("/")
@login_required
def index():
    return render_template("index.html")

@bp.route("/settings")
@login_required
def settings():
    redirect_non_map_admins()

    node_types = MapNodeType.query.all()

    return render_template("map/settings.html", node_types=node_types, title=page_title("Map settings"))

@bp.route("/node/create", methods=["GET", "POST"])
@login_required
def node_create():
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
    
    return render_template("map/node_create.html", form=form, title=page_title("Create map node type"))

@bp.route("/node/edit/<id>", methods=["GET", "POST"])
@login_required
def node_edit(id):
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
    return render_template("map/node_edit.html", form=form, node_type=node, title=page_title("Create map node type"))

@bp.route("/node/icon/<filename>")
@login_required
def node_icon(filename):
    return send_from_directory(app.config["MAPNODES_DIR"], filename)
