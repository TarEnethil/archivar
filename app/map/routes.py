from app import app, db
from app.helpers import page_title, flash_no_permission, admin_required
from app.map import bp
from app.map.forms import MapNodeTypeCreateForm, MapNodeTypeEditForm, MapSettingsForm, MapNodeForm, MapForm
from app.map.helpers import map_admin_required, map_node_filename, gen_node_type_choices, get_visible_nodes, map_changed, gen_submap_choices
from app.models import Map, MapNodeType, MapSetting, MapNode, WikiEntry
from app.wiki.helpers import gen_wiki_entry_choices
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, jsonify, send_from_directory
from flask_login import current_user, login_required
from os import path, remove
from PIL import Image

no_perm_url = "index"

@bp.route("/")
@login_required
def index():
    mapsettings = MapSetting.query.get(1)
    indexmap = Map.query.get(mapsettings.default_map)

    if not indexmap:
        if current_user.has_admin_role():
            maps = Map.query.all()

            if maps:
                flash("You need to select a default map to make this link work.", "warning")
                return redirect(url_for("map.settings"))
            else:
                flash("No map was created yet. You were redirected to the map creation.", "info")
                return redirect(url_for("map.create"))
        flash("The admin has not created a map yet.", "danger")
        return redirect(url_for("index"))

    if indexmap.is_visible == False and not current_user.has_admin_role():
        flash("This map is not visible.", "danger")
        return redirect(url_for("index"))

    return render_template("map/index.html", settings=mapsettings, map_=indexmap, title=page_title(indexmap.name))

@bp.route("/<int:id>")
@login_required
def view(id):
    map_ = Map.query.filter_by(id=id).first_or_404()
    settings = MapSetting.query.filter_by(id=1).first_or_404()

    if map_.is_visible == False and not current_user.has_admin_role():
        flash("This map is not visible.", "danger")
        return redirect(url_for("index"))

    return render_template("map/index.html", settings=settings, map_=map_, title=page_title(map_.name))

@bp.route("<int:id>/node/<int:n_id>")
@login_required
def view_with_node(id, n_id):
    mapsettings = MapSetting.query.get(1)
    map_ = Map.query.filter_by(id=id).first_or_404()
    node = MapNode.query.filter_by(id=n_id).first_or_404()

    if map_.is_visible == False and not current_user.has_admin_role():
        flash("This map is not visible.", "danger")
        return redirect(url_for("index"))

    if node.on_map != map_.id:
        flash("Map node {0} could not be found on this map".format(node.id), "danger")
        return render_template("map/index.html", settings=mapsettings, map_=map_, title=page_title(map_.name))

    return render_template("map/index.html", settings=mapsettings, map_=map_, jump_to_node=node.id, title=page_title(map_.name))

@bp.route("/create", methods=["GET", "POST"])
@login_required
@admin_required(no_perm_url)
def create():
    form = MapForm()
    form.submit.label.text = "Create Map"

    if form.validate_on_submit():
        maps = Map.query.all()

        new_map = Map(name=form.name.data, no_wrap=form.no_wrap.data, external_provider=form.external_provider.data, tiles_path=form.tiles_path.data, min_zoom=form.min_zoom.data, max_zoom=form.max_zoom.data, default_zoom=form.default_zoom.data)

        db.session.add(new_map)

        if not maps:
            mset = MapSetting.query.get(1)
            mset.default_map = new_map.id
            flash("This map was automatically selected as the default map. To change this, please visit the map settings.", "info")

        db.session.commit()

        flash("Map created.", "success")
        return redirect(url_for("map.view", id=new_map.id))

    return render_template("map/create.html", form=form, title=page_title("Create new map"))

# map specific settings
@bp.route("/<int:id>/settings", methods=["GET", "POST"])
@login_required
@admin_required(no_perm_url)
def map_settings(id):
    map_ = Map.query.filter_by(id=id).first_or_404()
    form = MapForm()
    form.submit.label.text = "Save Map"

    if form.validate_on_submit():
        map_.name = form.name.data
        map_.min_zoom = form.min_zoom.data
        map_.max_zoom = form.max_zoom.data
        map_.default_zoom = form.default_zoom.data
        map_.external_provider = form.external_provider.data
        map_.tiles_path = form.tiles_path.data
        map_.no_wrap = form.no_wrap.data
        map_.is_visible = form.is_visible.data

        db.session.commit()
        flash("Map settings have been changed.", "success")
        return redirect(url_for("map.view", id=map_.id))
    else:
        form.name.data = map_.name
        form.no_wrap.data = map_.no_wrap
        form.external_provider.data = map_.external_provider
        form.tiles_path.data = map_.tiles_path
        form.min_zoom.data = map_.min_zoom
        form.max_zoom.data = map_.max_zoom
        form.default_zoom.data = map_.default_zoom
        form.is_visible.data = map_.is_visible

        return render_template("map/edit.html", map=map_, form=form, title=page_title("Edit map '%s'" % map_.name))

# global map settings
@bp.route("/settings", methods=["GET", "POST"])
@login_required
@map_admin_required
def settings():
    form = MapSettingsForm()

    settings = MapSetting.query.get(1)

    if not current_user.has_admin_role():
        del form.default_map
    else:
        form.default_map.choices = gen_submap_choices("disabled")

    if form.validate_on_submit():
        settings.icon_anchor = form.icon_anchor.data
        settings.default_visible = form.default_visible.data
        settings.check_interval = form.check_interval.data

        if current_user.has_admin_role():
            settings.default_map = form.default_map.data

        db.session.commit()

        flash("Map settings have been changed.", "success")
    elif request.method == "GET":
        form.icon_anchor.data = settings.icon_anchor
        form.default_visible.data = settings.default_visible
        form.check_interval.data = settings.check_interval

        if current_user.has_admin_role():
            form.default_map.data = settings.default_map

    node_types = MapNodeType.query.all()

    return render_template("map/settings.html", form=form, settings=settings, node_types=node_types, title=page_title("Map Settings"))

@bp.route("/list")
@login_required
@admin_required(no_perm_url)
def list():
    maps = Map.query.all()

    return render_template("map/list.html", maps=maps, title=page_title("List of maps"))

@bp.route("/node/create/<int:map_id>/<x>/<y>", methods=["GET", "POST"])
@login_required
def node_create(map_id, x, y):
    Map.query.filter_by(id=map_id).first_or_404()

    form = MapNodeForm()
    form.submit.label.text = "Create Node"

    if not current_user.is_map_admin():
        del form.is_visible

    if not current_user.has_admin_role():
        del form.submap
    else:
        form.submap.choices = gen_submap_choices()

    form.coord_x.data = x
    form.coord_y.data = y

    form.node_type.choices = gen_node_type_choices()
    form.wiki_entry.choices = gen_wiki_entry_choices()

    if form.validate_on_submit():
        new_node = MapNode(name=form.name.data, description=form.description.data, node_type=form.node_type.data, coord_x=form.coord_x.data, coord_y=form.coord_y.data, wiki_entry_id=form.wiki_entry.data, on_map=map_id)

        if current_user.is_map_admin():
            new_node.is_visible = form.is_visible.data

            if new_node.is_visible:
                message = "Node was created."
            else:
                message = "Node was created, it is only visible to map admins."
        else:
            msetting = MapSetting.query.get(1)
            new_node.is_visible = msetting.default_visible

            if new_node.is_visible:
                message = "Node was created."
            else:
                message = "Node was created. Until approved, it is only visible to map admins and you."

        if current_user.has_admin_role():
            new_node.submap = form.submap.data

        db.session.add(new_node)
        db.session.commit()

        map_changed(new_node.on_map)

        return jsonify(data={'success' : True, 'message': message})
    elif request.method == "POST":
        return jsonify(data={'success' : False, 'message': "Form validation error", 'errors': form.errors})
    else:
        if current_user.is_map_admin():
            msetting = MapSetting.query.get(1)
            form.is_visible.data = msetting.default_visible

    return render_template("map/node_create.html", form=form, x=x, y=y)

@bp.route("/node/edit/<id>", methods=["GET", "POST"])
@login_required
def node_edit(id):
    form = MapNodeForm()
    form.submit.label.text = "Save Node"

    if not current_user.is_map_admin():
        del form.is_visible

    if not current_user.has_admin_role():
        del form.submap
    else:
        form.submap.choices = gen_submap_choices()

    form.node_type.choices = gen_node_type_choices()

    node = MapNode.query.filter_by(id=id).first_or_404()

    # TODO: make custom decorators for this?
    if not current_user.has_admin_role() and current_user.has_map_role() and node.is_visible == False and node.created_by.has_admin_role():
        flash_no_permission()
        return redirect(url_for(no_perm_url))

    if not current_user.is_map_admin() and node.is_visible == False and not node.created_by == current_user:
        flash_no_permission()
        redirect(url_for(no_perm_url))

    wiki_entry_ok = True

    if node.wiki_entry_id != 0 and node.wiki_entry_id != None:
        wentry = WikiEntry.query.filter_by(id=node.wiki_entry_id).first()

        if not wentry:
            wiki_entry_ok = False
        else:
            if not current_user.has_admin_role() and current_user.is_wiki_admin() and wentry.is_visible == False and wentry.created_by.has_admin_role():
                wiki_entry_ok = False

            if not current_user.is_wiki_admin() and wentry.is_visible == False and not wentry.created_by == current_user:
                wiki_entry_ok = False

    if wiki_entry_ok == True:
        form.wiki_entry.choices = gen_wiki_entry_choices()
    else:
        form.wiki_entry.label.text = "(wiki entry is invisible to you and can not be changed.)"
        form.wiki_entry.render_kw = {"disabled": "disabled"};
        form.wiki_entry.choices = [(0, "disabled")]

    if form.validate_on_submit():
        node.name = form.name.data
        node.description = form.description.data
        node.node_type = form.node_type.data

        node.coord_x = form.coord_x.data
        node.coord_y = form.coord_y.data

        if wiki_entry_ok == True:
            node.wiki_entry_id = form.wiki_entry.data

        if current_user.is_map_admin():
            node.is_visible = form.is_visible.data

        if current_user.has_admin_role():
            node.submap = form.submap.data

        db.session.commit()
        map_changed(node.on_map)

        return jsonify(data={'success' : True, 'message': "Node was edited."})
    elif request.method == "POST":
        return jsonify(data={'success' : False, 'message': "Form validation error", 'errors': form.errors})

    form.name.data = node.name
    form.description.data = node.description
    form.node_type.data = node.node_type

    form.coord_x.data = node.coord_x
    form.coord_y.data = node.coord_y

    if wiki_entry_ok == True:
        form.wiki_entry.data = node.wiki_entry_id

    if current_user.is_map_admin():
        form.is_visible.data = node.is_visible

    if current_user.has_admin_role():
        form.submap.data = node.submap

    return render_template("map/node_edit.html", form=form, node=node)

@bp.route("/node/delete/<id>", methods=["POST"])
@login_required
def node_delete(id):
    if not current_user.is_map_admin():
        return jsonify(data={'success': False, 'message': "You dont have the necessary role to do that."})

    node = MapNode.query.get(id)

    if not node:
        return jsonify(data={'success': False, 'message': "No such id to delete."})

    map_id = node.on_map

    db.session.delete(node)
    db.session.commit()

    map_changed(map_id)

    return jsonify(data={"success": True, 'message': "Node was deleted."})

@bp.route("/node_type/create", methods=["GET", "POST"])
@login_required
@admin_required(no_perm_url)
def node_type_create():
    form = MapNodeTypeCreateForm()

    if form.validate_on_submit():
        filename = map_node_filename(form.icon.data.filename)
        filepath = path.join(app.config["MAPNODES_DIR"], filename)
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
@map_admin_required
def node_type_edit(id):
    form = MapNodeTypeEditForm()
    node = MapNodeType.query.filter_by(id=id).first_or_404()

    if form.validate_on_submit():
        node.name = form.name.data
        node.description = form.description.data

        if form.icon.data:
            new_filename = map_node_filename(form.icon.data.filename)
            filepath = path.join(app.config["MAPNODES_DIR"], new_filename)
            form.icon.data.save(filepath)

            icon = Image.open(filepath)
            width, height = icon.size

            remove(path.join(app.config["MAPNODES_DIR"], node.icon_file))

            node.icon_file = new_filename
            node.icon_width = width
            node.icon_height = height

        db.session.commit()
        flash('"' + form.name.data + '" was successfully edited.', "success")
        return redirect(url_for('map.settings'))
    elif request.method == "GET":
        form.name.data = node.name
        form.description.data = node.description

    return render_template("map/node_type_edit.html", form=form, node_type=node, title=("Edit map node type '%s'" % node.name))

@bp.route("/node_type/json")
@login_required
def node_type_json():
    all_types = MapNodeType.query.all()

    all_types_dict = {}

    for node_type in all_types:
        all_types_dict[node_type.id] = node_type.to_dict()

    return jsonify(all_types_dict)

@bp.route("<int:id>/node/json")
@login_required
def node_json(id):
    nodes = get_visible_nodes(id)

    nodes_dict = {}

    for node in nodes:
        nodes_dict[node.id] = node.to_dict()

    return jsonify(nodes_dict)

@bp.route("/node_type/icon/<filename>")
@login_required
def node_type_icon(filename):
    return send_from_directory(app.config["MAPNODES_DIR"], filename)

@bp.route("/<int:id>/last_change")
@login_required
def last_change(id):
    mset = Map.query.filter_by(id=id).first_or_404()

    return jsonify({'last_change' : str(mset.last_change) })

@bp.route("/tile/<path:filename>")
@login_required
def tile(filename):
    return send_from_directory(app.config["MAPTILES_DIR"], filename)

@bp.route("/sidebar/<int:m_id>", methods=["GET"])
@login_required
def sidebar(m_id):
    nodes = get_visible_nodes(m_id)

    d = {}
    for n in nodes:
        d[n.id] = n.sidebar_dict();

    return jsonify(d)

@bp.route("/sidebar/maps", methods=["GET"])
@login_required
def sidebar_maps():
    cats = Map.query.order_by(Map.id.asc()).all()

    d = {}

    for c in cats:
        d[c.id] = c.to_dict()

    return jsonify(d);
