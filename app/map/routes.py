from app import db
from app.decorators import admin_required, moderator_required
from app.helpers import page_title, deny_access
from app.map import bp
from app.map.forms import MapNodeTypeCreateForm, MapNodeTypeEditForm, MapSettingsForm, MapNodeForm, MapForm
from app.map.helpers import upload_node_icon, delete_node_icon, gen_node_type_choices, \
    map_changed, gen_submap_choices
from app.map.models import Map, MapNodeType, MapSetting, MapNode
from app.wiki.helpers import gen_wiki_entry_choices
from flask import render_template, flash, redirect, url_for, request, jsonify, send_from_directory, current_app
from flask_login import current_user, login_required

no_perm_url = "main.index"


@bp.route("/")
@login_required
def index():
    mapsettings = MapSetting.query.get(1)
    indexmap = Map.query.get(mapsettings.default_map)

    if not indexmap:
        maps = Map.query.all()

        if maps and current_user.is_at_least_moderator():
            flash("You need to select a default map to make this link work.", "warning")
            return redirect(url_for("map.settings"))
        elif current_user.is_admin():
            flash("No map was created yet. You were redirected to the map creation.", "info")
            return redirect(url_for("map.create"))
        else:
            flash("The admin has not created a map yet.", "danger")
            return redirect(url_for(no_perm_url))

    return redirect(indexmap.view_url())


@bp.route("/<int:id>/<string:name>")
@bp.route("/<int:id>")
@login_required
def view(id, name=None):
    map_ = Map.query.filter_by(id=id).first_or_404()
    settings = MapSetting.query.filter_by(id=1).first_or_404()

    if not map_.is_viewable_by_user():
        return deny_access(no_perm_url)

    return render_template("map/index.html", settings=settings, map_=map_, title=page_title(map_.name))


@bp.route("<int:id>/<string:m_name>/node/<int:n_id>/<string:n_name>")
@bp.route("<int:id>/node/<int:n_id>")
@login_required
def view_with_node(id, n_id, m_name=None, n_name=None):
    mapsettings = MapSetting.query.get(1)
    map_ = Map.query.filter_by(id=id).first_or_404()
    node = MapNode.query.filter_by(id=n_id).first_or_404()

    if not map_.is_viewable_by_user():
        return deny_access(no_perm_url)

    if node.on_map != map_.id:
        flash(f"Map node '{node.id}' could not be found on this map", "danger")
        return redirect(map_.view_url())

    return render_template("map/index.html", settings=mapsettings, map_=map_, jump_to_node=node.id,
                           title=page_title(map_.name))


@bp.route("/create", methods=["GET", "POST"])
@login_required
@admin_required(no_perm_url)
def create():
    form = MapForm()
    form.submit.label.text = "Create Map"

    if form.validate_on_submit():
        maps = Map.query.all()

        new_map = Map(name=form.name.data,
                      no_wrap=form.no_wrap.data,
                      external_provider=form.external_provider.data,
                      tiles_path=form.tiles_path.data,
                      min_zoom=form.min_zoom.data,
                      max_zoom=form.max_zoom.data,
                      default_zoom=form.default_zoom.data)

        db.session.add(new_map)

        if not maps:
            mset = MapSetting.query.get(1)
            mset.default_map = new_map.id
            flash("This map was automatically selected as the default map.", "info")

        db.session.commit()

        flash("Map created.", "success")
        return redirect(new_map.view_url())

    return render_template("map/create.html", form=form, title=page_title("Add Map"))


# map specific settings
@bp.route("/<int:id>/<string:name>/settings", methods=["GET", "POST"])
@login_required
def map_settings(id, name=None):
    map_ = Map.query.filter_by(id=id).first_or_404()

    if not map_.is_editable_by_user():
        return deny_access(no_perm_url)

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
        return redirect(map_.view_url())
    else:
        form.name.data = map_.name
        form.no_wrap.data = map_.no_wrap
        form.external_provider.data = map_.external_provider
        form.tiles_path.data = map_.tiles_path
        form.min_zoom.data = map_.min_zoom
        form.max_zoom.data = map_.max_zoom
        form.default_zoom.data = map_.default_zoom
        form.is_visible.data = map_.is_visible

        return render_template("map/edit.html", map=map_, form=form,
                               title=page_title(f"Edit Map '{map_.name}'"))


# global map settings
@bp.route("/settings", methods=["GET", "POST"])
@login_required
@moderator_required(no_perm_url)
def settings():
    form = MapSettingsForm()

    settings = MapSetting.query.get(1)

    form.default_map.choices = gen_submap_choices("disabled", ensure=settings.default_map)

    if form.validate_on_submit():
        settings.icon_anchor = form.icon_anchor.data
        settings.default_visible = form.default_visible.data
        settings.check_interval = form.check_interval.data
        settings.default_map = form.default_map.data

        db.session.commit()

        flash("Map settings have been changed.", "success")
    elif request.method == "GET":
        form.icon_anchor.data = settings.icon_anchor
        form.default_visible.data = settings.default_visible
        form.check_interval.data = settings.check_interval
        form.default_map.data = settings.default_map

    node_types = MapNodeType.query.all()

    return render_template("map/settings.html", form=form, settings=settings, node_types=node_types,
                           title=page_title("Map Settings"))


@bp.route("/list")
@login_required
def list():
    maps = Map.get_visible_items(include_hidden_for_user=True)

    return render_template("map/list.html", maps=maps, title=page_title("List of Maps"))


@bp.route("/node/create/<int:map_id>/<x>/<y>", methods=["GET", "POST"])
@login_required
def node_create(map_id, x, y):
    map_ = Map.query.filter_by(id=map_id).first_or_404()

    if not map_.is_viewable_by_user():
        flash("No permission to create Location on this map.", "danger")
        return render_template("map/ajax_error.html")

    form = MapNodeForm()
    form.submit.label.text = "Create Location"

    form.submap.choices = gen_submap_choices()

    form.coord_x.data = x
    form.coord_y.data = y

    form.node_type.choices = gen_node_type_choices()
    form.wiki_entry.choices = gen_wiki_entry_choices()

    if form.validate_on_submit():
        new_node = MapNode(name=form.name.data,
                           description=form.description.data,
                           node_type=form.node_type.data,
                           coord_x=form.coord_x.data,
                           coord_y=form.coord_y.data,
                           on_map=map_id)

        new_node.is_visible = form.is_visible.data
        new_node.submap = form.submap.data

        if form.wiki_entry.data != 0:
            new_node.wiki_entry_id = form.wiki_entry.data

        db.session.add(new_node)
        db.session.commit()

        map_changed(new_node.on_map)

        message = "The Location was added."

        return jsonify(data={'success': True, 'message': message})
    elif request.method == "POST":
        return jsonify(data={'success': False, 'message': "Form validation error", 'errors': form.errors})
    else:
        form.is_visible.data = True

    return render_template("map/node_create.html", form=form, x=x, y=y)


@bp.route("/node/edit/<id>", methods=["GET", "POST"])
@login_required
def node_edit(id):
    node = MapNode.query.get(id)

    if not node:
        flash("Location could not be found..", "danger")
        return render_template("map/ajax_error.html")

    if not node.is_editable_by_user():
        flash("No permission to edit this Location.", "danger")
        return render_template("map/ajax_error.html")

    form = MapNodeForm()
    form.submit.label.text = "Save Location"

    if not node.is_hideable_by_user():
        del form.is_visible

    form.submap.choices = gen_submap_choices(ensure=node.sub_map)
    form.node_type.choices = gen_node_type_choices()
    form.wiki_entry.choices = gen_wiki_entry_choices(ensure=node.wiki_entry)

    if form.validate_on_submit():
        node.name = form.name.data
        node.description = form.description.data
        node.node_type = form.node_type.data

        node.coord_x = form.coord_x.data
        node.coord_y = form.coord_y.data

        if form.wiki_entry.data == 0:
            node.wiki_entry = None
        else:
            node.wiki_entry_id = form.wiki_entry.data

        if node.is_hideable_by_user():
            node.is_visible = form.is_visible.data

        node.submap = form.submap.data

        db.session.commit()
        map_changed(node.on_map)

        return jsonify(data={'success': True, 'message': "Location was edited."})
    elif request.method == "POST":
        return jsonify(data={'success': False, 'message': "Form validation error", 'errors': form.errors})

    form.name.data = node.name
    form.description.data = node.description
    form.node_type.data = node.node_type

    form.coord_x.data = node.coord_x
    form.coord_y.data = node.coord_y

    form.wiki_entry.data = node.wiki_entry_id

    if node.is_hideable_by_user():
        form.is_visible.data = node.is_visible

    form.submap.data = node.submap

    return render_template("map/node_edit.html", form=form, node=node)


@bp.route("/node/delete/<id>", methods=["POST"])
@login_required
def node_delete(id):
    node = MapNode.query.get(id)

    if not node:
        return jsonify(data={'success': False, 'message': "Location could not be found."})

    if not node.is_deletable_by_user():
        return jsonify(data={'success': False, 'message': "You dont have the necessary role to do that."})

    map_id = node.on_map

    db.session.delete(node)
    db.session.commit()

    map_changed(map_id)

    return jsonify(data={"success": True, 'message': "Location was deleted."})


@bp.route("/node_type/create", methods=["GET", "POST"])
@login_required
@moderator_required(no_perm_url)
def node_type_create():
    form = MapNodeTypeCreateForm()

    if form.validate_on_submit():
        success, filename, width, height = upload_node_icon(form.icon.data)

        new_map_node_type = MapNodeType(name=form.name.data,
                                        description=form.description.data,
                                        icon_file=filename,
                                        icon_width=width,
                                        icon_height=height)

        if success is False:
            flash("Error while creating node type.", "error")
        else:
            db.session.add(new_map_node_type)
            db.session.commit()
            flash(f"'{form.name.data}' was successfully created.", "success")
            return redirect(url_for('map.settings'))

    return render_template("map/node_type_create.html", form=form, title=page_title("Create location type"))


@bp.route("/node_type/edit/<id>", methods=["GET", "POST"])
@login_required
@moderator_required(no_perm_url)
def node_type_edit(id):
    form = MapNodeTypeEditForm()
    node = MapNodeType.query.filter_by(id=id).first_or_404()

    if form.validate_on_submit():
        node.name = form.name.data
        node.description = form.description.data

        success = True
        if form.icon.data:
            success, filename, width, height = upload_node_icon(form.icon.data)

            if success:
                delete_node_icon(node.icon_file)

            node.icon_file = filename
            node.icon_width = width
            node.icon_height = height

        if success is False:
            flash("Error while editing node type.", "error")
        else:
            db.session.commit()
            flash(f"'{form.name.data}' was successfully edited.", "success")
            return redirect(url_for('map.settings'))
    elif request.method == "GET":
        form.name.data = node.name
        form.description.data = node.description

    return render_template("map/node_type_edit.html", form=form, node_type=node,
                           title=(f"Edit location type '{node.name}'"))


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
    map_ = Map.query.filter_by(id=id).first_or_404()
    nodes = map_.get_nodes()

    nodes_dict = {}

    for node in nodes:
        nodes_dict[node.id] = node.to_dict()

    return jsonify(nodes_dict)


@bp.route("/node_type/icon/<filename>")
def node_type_icon(filename):
    return send_from_directory(current_app.config["MAPNODES_DIR"], filename)


@bp.route("/<int:id>/last_change")
@login_required
def last_change(id):
    mset = Map.query.filter_by(id=id).first_or_404()

    return jsonify({'last_change': str(mset.last_change)})


@bp.route("/tile/<path:filename>")
def tile(filename):
    return send_from_directory(current_app.config["MAPTILES_DIR"], filename)


@bp.route("/sidebar/<int:m_id>", methods=["GET"])
@login_required
def sidebar(m_id):
    map_ = Map.query.filter_by(id=id).first_or_404()
    nodes = map_.get_nodes()

    d = {}
    for n in nodes:
        d[n.id] = n.sidebar_dict()

    return jsonify(d)


@bp.route("/sidebar/maps", methods=["GET"])
@login_required
def sidebar_maps():
    cats = Map.get_query_for_visible_items(include_hidden_for_user=True).order_by(Map.id.asc()).all()

    d = {}

    for c in cats:
        d[c.id] = c.to_dict()

    return jsonify(d)
