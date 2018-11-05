from app import app, db
from app.helpers import page_title, flash_no_permission
from app.models import MediaSetting, MediaItem, MediaCategory, User, Role
from app.media import bp
from app.media.forms import SettingsForm, MediaItemCreateForm, MediaItemEditForm, CategoryForm
from app.media.helpers import redirect_non_media_admins, get_media, gen_media_category_choices, media_filename
from flask import render_template, flash, redirect, url_for, request, jsonify, send_from_directory
from flask_login import login_required, current_user
from sqlalchemy import not_, and_, or_
from os import path, remove, stat

no_perm = "media.index"

@bp.route("/dummy", methods=["GET"])
@login_required
def dummy():
    return redirect(url_for("index"))

@bp.route("/index", methods=["GET"])
@bp.route("/list", methods=["GET"])
@bp.route("/", methods=["GET"])
@login_required
def index():
    media = get_media()

    return render_template("media/index.html", media=media, title=page_title("Media"))

@bp.route("/view/<int:id>", methods=["GET"])
@login_required
def view(id):
    item = MediaItem.query.filter_by(id=id).first_or_404()

    if not current_user.is_event_admin() and item.is_visible == False and not item.created_by == current_user:
        flash_no_permission()
        return redirect(url_for(no_perm))

    if not current_user.has_admin_role() and current_user.has_media_role() and item.is_visible == False and item.created_by.has_admin_role():
        flash_no_permission()
        return redirect(url_for(no_perm))

    return render_template("media/view.html", item=item, title=page_title("View file"))

@bp.route("/list/category-<int:c_id>", methods=["GET"])
@login_required
def list_by_cat(c_id):
    m = MediaCategory.query.filter_by(id=c_id).first_or_404()
    files = get_media(c_id)

    return render_template("media/list.html", media=files, catname=m.name, title=page_title("View files in category"))

@bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    settings = MediaSetting.query.get(1)
    form = MediaItemCreateForm()
    form.category.choices = gen_media_category_choices()

    if not current_user.is_media_admin():
        del form.is_visible

    if form.validate_on_submit():
        filename = media_filename(form.file.data.filename)

        filepath = path.join(app.config["MEDIA_DIR"], filename)
        form.file.data.save(filepath)

        size = stat(filepath).st_size

        new_media = MediaItem(name=form.name.data, filename=filename, filesize=size, category_id=form.category.data, created_by_id=current_user.id)

        if current_user.is_media_admin():
            new_media.is_visible = form.is_visible.data
        else:
            new_media.is_visible = settings.default_visible

        db.session.add(new_media)
        db.session.commit()

        flash("Upload successful.", "success")
        return redirect(url_for("media.index"))

    return render_template("media/upload.html", form=form, title=page_title("Upload file"))

@bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    item = MediaItem.query.filter_by(id=id).first_or_404()

    form = MediaItemEditForm()
    form.category.choices = gen_media_category_choices()

    if not current_user.has_admin_role() and current_user.has_media_role() and item.is_visible == False and item.created_by.has_admin_role():
        flash_no_permission()
        return redirect(url_for(no_perm))

    if not current_user.is_media_admin() and item.is_visible == False and not item.created_by == current_user:
        flash_no_permission()
        return redirect(url_for(no_perm))

    if not current_user.is_media_admin():
        del form.is_visible

    form.file.label.text = "Replace with file"

    if form.validate_on_submit():
        item.name = form.name.data
        item.category_id = form.category.data
        item.edited_by_id = current_user.id

        if current_user.is_event_admin():
            item.is_visible = form.is_visible.data

        if form.file.data:
            remove(path.join(app.config["MEDIA_DIR"], item.filename))

            filepath = path.join(app.config["MEDIA_DIR"], item.filename)
            form.file.data.save(filepath)

            item.filesize = stat(filepath).st_size

        db.session.commit()

        flash("File was edited.", "success")

        return redirect(url_for("media.index"))
    elif request.method == "GET":
        form.name.data = item.name
        form.category.data = item.category_id

        if current_user.is_media_admin():
            form.is_visible.data = item.is_visible

    return render_template("media/edit.html", form=form, title=page_title("Edit file"))

@bp.route("/category/create", methods=["GET", "POST"])
@login_required
def category_create():
    deny_access = redirect_non_media_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    heading = "Create new media category"
    form = CategoryForm()

    if form.validate_on_submit():
        new_category = MediaCategory(name=form.name.data)

        db.session.add(new_category)
        db.session.commit()

        flash("Category created.", "success")
        return redirect(url_for("media.settings"))

    return render_template("media/category.html", form=form, heading=heading, title=page_title(heading))

@bp.route("/category/edit/<int:id>", methods=["GET", "POST"])
@login_required
def category_edit(id):
    deny_access = redirect_non_media_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    heading = "Edit media category"
    form = CategoryForm()

    category = MediaCategory.query.filter_by(id=id).first_or_404()

    if form.validate_on_submit():
        category.name = form.name.data

        db.session.commit()

        flash("Media category edited.", "success")
        return redirect(url_for("media.settings"))
    elif request.method == "GET":
        form.name.data = category.name

    return render_template("media/category.html", form=form, heading=heading, title=page_title(heading))

@bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    deny_access = redirect_non_media_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    settings = MediaSetting.query.get(1)
    form = SettingsForm()

    if form.validate_on_submit():
        settings.default_visible = form.default_visible.data

        db.session.commit()

        flash("Event settings have been changed.", "success")
    elif request.method == "GET":
        form.default_visible.data = settings.default_visible

    categories = MediaCategory.query.all()

    return render_template("media/settings.html", categories=categories, form=form, title=page_title("Media settings"))

@bp.route("/sidebar", methods=["GET"])
@login_required
def sidebar():
    if current_user.has_admin_role():
        entries = MediaItem.query
    elif current_user.has_media_role():
        admins = User.query.filter(User.roles.contains(Role.query.get(1)))
        admin_ids = [a.id for a in admins]
        entries = MediaItem.query.filter(not_(and_(MediaItem.is_visible == False, MediaItem.created_by_id.in_(admin_ids))))
    else:
        entries = MediaItem.query.filter(or_(MediaItem.is_visible == True, MediaItem.created_by_id == current_user.id))

    entries = entries.with_entities(MediaItem.id, MediaItem.name, MediaItem.is_visible).order_by(MediaItem.name.asc()).all()

    return jsonify(entries)

@bp.route("/serve/<filename>")
@login_required
def serve_file(filename):
    return send_from_directory(app.config["MEDIA_DIR"], filename)