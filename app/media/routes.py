from app import db
from app.helpers import page_title, flash_no_permission
from app.media import bp
from app.media.forms import SettingsForm, MediaItemCreateForm, MediaItemEditForm, CategoryForm
from app.media.helpers import media_admin_required, get_media, gen_media_category_choices, media_filename, generate_thumbnail
from app.media.models import MediaSetting, MediaItem, MediaCategory
from app.user.models import User, Role
from flask import render_template, flash, redirect, url_for, request, jsonify, send_from_directory, current_app
from flask_login import login_required, current_user
from sqlalchemy import not_, and_, or_
from os import path, remove, stat

no_perm_url = "media.index"

@bp.route("/index", methods=["GET"])
@bp.route("/list", methods=["GET"])
@bp.route("/", methods=["GET"])
@login_required
def index():
    media = get_media()

    return render_template("media/index.html", media=media, title=page_title("Media"))

@bp.route("/view/<int:id>/<string:name>", methods=["GET"])
@bp.route("/view/<int:id>", methods=["GET"])
@login_required
def view(id, name=None):
    item = MediaItem.query.filter_by(id=id).first_or_404()

    # TODO: write custom decorator for this?
    if not current_user.is_event_admin() and item.is_visible == False and not item.created_by == current_user:
        flash_no_permission()
        return redirect(url_for(no_perm_url))

    if not current_user.has_admin_role() and current_user.has_media_role() and item.is_visible == False and item.created_by.has_admin_role():
        flash_no_permission()
        return redirect(url_for(no_perm_url))

    return render_template("media/view.html", item=item, title=page_title("View File"))

@bp.route("/list/category-<int:c_id>/<string:c_name>", methods=["GET"])
@login_required
def list_by_cat(c_id, c_name=None):
    m = MediaCategory.query.filter_by(id=c_id).first_or_404()
    files = get_media(c_id)

    return render_template("media/list.html", media=files, cat=m, title=page_title("View Files in Category '{}'".format(m.name)))

@bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    settings = MediaSetting.query.get(1)
    form = MediaItemCreateForm()
    form.category.choices = gen_media_category_choices()

    # check if ajax-GET param was set, which means we must return json
    ajax = request.args.get("ajax") != None

    if not current_user.is_media_admin():
        del form.is_visible

    if form.validate_on_submit():
        filename = media_filename(form.file.data.filename)

        filepath = path.join(current_app.config["MEDIA_DIR"], filename)
        form.file.data.save(filepath)

        size = stat(filepath).st_size

        new_media = MediaItem(name=form.name.data, filename=filename, filesize=size, category_id=form.category.data)

        if current_user.is_media_admin():
            new_media.is_visible = form.is_visible.data
        else:
            new_media.is_visible = settings.default_visible

        msg = "Upload successful."
        level = "success"

        if new_media.is_image():
            if generate_thumbnail(filename) == False:
                msg = "Upload successful, but there were errors."
                level = "warning"

        db.session.add(new_media)
        db.session.commit()

        flash(msg, level)

        # uploaded succeeded, send back info about new media
        if ajax:
            return jsonify(data={'success' : True,
                                'html' : render_template("media/upload_success.html", item=new_media),
                                'media_info' : {
                                        'id' : new_media.id,
                                        'name' : new_media.name,
                                        'view_url' : new_media.view_url(),
                                        'serve_url' : new_media.serve_url(),
                                        'thumbnail_url' : new_media.thumbnail_url(),
                                        'is_image' : new_media.is_image()
                                    }
                                })
        else:
            return redirect(new_media.view_url())

    elif ajax and request.method == "POST":
        # the form validation failed, send back the form with displayed errors
        flash("There was an error processing the upload.", "danger")
        return jsonify(data={'success' : False, 'html': render_template("media/upload_raw.html", form=form, max_filesize=current_app.config["MAX_CONTENT_LENGTH"]) })
    elif request.method == "GET":
        if current_user.is_media_admin() and settings.default_visible:
            form.is_visible.data = True

        # pre-select category if get-param was passed
        category_id = request.args.get("category")

        # will do nothing if var is not an int or not in choices
        if category_id:
            try:
                form.category.data = int(category_id)
            except:
                pass

    # non-ajax: return the full page
    template = "media/upload.html"

    # ajax: return only the form
    if ajax:
        template = "media/upload_raw.html"

    return render_template(template, form=form, max_filesize=current_app.config["MAX_CONTENT_LENGTH"], title=page_title("Upload File"))

@bp.route("/edit/<int:id>/<string:name>", methods=["GET", "POST"])
@login_required
def edit(id, name=None):
    item = MediaItem.query.filter_by(id=id).first_or_404()

    form = MediaItemEditForm()
    form.category.choices = gen_media_category_choices()

    # TODO: write custom decorator for this?
    if not current_user.has_admin_role() and current_user.has_media_role() and item.is_visible == False and item.created_by.has_admin_role():
        flash_no_permission()
        return redirect(url_for(no_perm_url))

    if not current_user.is_media_admin() and item.is_visible == False and not item.created_by == current_user:
        flash_no_permission()
        return redirect(url_for(no_perm_url))

    if not current_user.is_media_admin():
        del form.is_visible

    form.file.label.text = "Replace with file"

    if form.validate_on_submit():
        item.name = form.name.data
        item.category_id = form.category.data

        if current_user.is_event_admin():
            item.is_visible = form.is_visible.data

        msg = "File was edited."
        level = "success"

        if form.file.data:
            filepath = path.join(current_app.config["MEDIA_DIR"], item.filename)
            # overrides former file
            form.file.data.save(filepath)

            item.filesize = stat(filepath).st_size

            if item.is_image():
                # overrides former thumbnail
                if generate_thumbnail(item.filename) == False:
                    msg = "File was edited, but there were errors."
                    level = "warning"

        db.session.commit()

        flash(msg, level)

        return redirect(item.view_url())
    elif request.method == "GET":
        form.name.data = item.name
        form.category.data = item.category_id

        if current_user.is_media_admin():
            form.is_visible.data = item.is_visible

    return render_template("media/edit.html", form=form, title=page_title("Edit File '{}'".format(item.name)))

@bp.route("/delete/<int:id>/<string:name>", methods=["GET"])
@login_required
def delete(id, name=None):
    item = MediaItem.query.filter_by(id=id).first_or_404()

    if not current_user.is_event_admin() and item.is_visible == False and not item.created_by == current_user:
        flash_no_permission()
        return redirect(url_for(no_perm_url))

    if not current_user.has_admin_role() and current_user.has_media_role() and item.is_visible == False and item.created_by.has_admin_role():
        flash_no_permission()
        return redirect(url_for(no_perm_url))

    remove(path.join(current_app.config["MEDIA_DIR"], item.filename))

    if item.is_image():
        remove(path.join(current_app.config["MEDIA_DIR"], "thumbnails", item.filename))

    db.session.delete(item)
    db.session.commit()

    flash("Media item was deleted.", "success")
    return redirect(url_for('media.index'))

@bp.route("/category/create", methods=["GET", "POST"])
@login_required
@media_admin_required
def category_create():
    heading = "Add Media Category"
    form = CategoryForm()
    form.submit.label.text = "Create Category"

    if form.validate_on_submit():
        new_category = MediaCategory(name=form.name.data)

        db.session.add(new_category)
        db.session.commit()

        flash("Category created.", "success")
        return redirect(url_for("media.settings"))

    return render_template("media/category.html", form=form, heading=heading, title=page_title(heading))

@bp.route("/category/edit/<int:id>/<string:name>", methods=["GET", "POST"])
@login_required
@media_admin_required
def category_edit(id, name=None):
    form = CategoryForm()
    form.submit.label.text = "Save Category"

    category = MediaCategory.query.filter_by(id=id).first_or_404()
    heading = "Edit Media Category '%s'" % category.name

    if form.validate_on_submit():
        category.name = form.name.data

        db.session.commit()

        flash("Media category edited.", "success")
        return redirect(url_for("media.settings"))
    elif request.method == "GET":
        form.name.data = category.name

    return render_template("media/category.html", category=category, form=form, heading=heading, title=page_title(heading))

@bp.route("/settings", methods=["GET", "POST"])
@login_required
@media_admin_required
def settings():
    settings = MediaSetting.query.get(1)
    form = SettingsForm()

    if form.validate_on_submit():
        settings.default_visible = form.default_visible.data

        db.session.commit()

        flash("Event settings have been changed.", "success")
    elif request.method == "GET":
        form.default_visible.data = settings.default_visible

    categories = MediaCategory.query.all()

    return render_template("media/settings.html", settings=settings, categories=categories, form=form, title=page_title("Media Settings"))

@bp.route("/sidebar/<int:c_id>", methods=["GET"])
@login_required
def sidebar(c_id):
    if current_user.has_admin_role():
        entries = MediaItem.query
    elif current_user.has_media_role():
        admins = User.query.filter(User.roles.contains(Role.query.get(1)))
        admin_ids = [a.id for a in admins]
        entries = MediaItem.query.filter(not_(and_(MediaItem.is_visible == False, MediaItem.created_by_id.in_(admin_ids))))
    else:
        entries = MediaItem.query.filter(or_(MediaItem.is_visible == True, MediaItem.created_by_id == current_user.id))

    entries = entries.filter_by(category_id=c_id).order_by(MediaItem.name.asc()).all()

    d = {}
    for m in entries:
        d[m.id] = m.to_dict();

    return jsonify(d)

@bp.route("/sidebar/categories", methods=["GET"])
@login_required
def sidebar_categories():
    cats = MediaCategory.query.order_by(MediaCategory.name.asc()).all()

    d = {}

    for c in cats:
        d[c.id] = c.to_dict()

    return jsonify(d);

@bp.route("/serve/<filename>")
@login_required
def serve_file(filename):
    return send_from_directory(current_app.config["MEDIA_DIR"], filename)

@bp.route("/serve-thumb/<filename>")
@login_required
def serve_thumbnail(filename):
    return send_from_directory(path.join(current_app.config["MEDIA_DIR"], "thumbnails"), filename)