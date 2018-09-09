from flask import render_template, flash, redirect, url_for, request, jsonify
from app import db
from app.wiki import bp
from app.helpers import page_title, redirect_non_admins, redirect_non_wiki_admins, flash_no_permission, prepare_wiki_nav, search_wiki_tag, search_wiki_text, prepare_search_result
from app.wiki.forms import WikiEntryForm, WikiSettingsForm, WikiSearchForm
from app.models import User, Role, GeneralSetting, Character, Party, WikiEntry, WikiSetting
from flask_login import current_user, login_required
from datetime import datetime

no_perm = "wiki.index"

@bp.route("/", methods=["GET"])
@login_required
def index():
    return redirect(url_for("wiki.view", id=1))

@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = WikiEntryForm()

    if not current_user.is_wiki_admin():
        del form.is_visible

    if not current_user.has_admin_role():
        del form.dm_content

    if form.validate_on_submit():
        if current_user.is_wiki_admin():
            visible = form.is_visible.data
        else:
            ws = WikiSetting.query.get(1)
            visible = ws.default_visible

        dm_content = ""

        if current_user.has_admin_role():
            dm_content = form.dm_content.data

        entry = WikiEntry(title=form.title.data, content=form.content.data, category=form.category.data, tags=form.tags.data, is_visible=visible, dm_content=dm_content, created_by=current_user)

        db.session.add(entry)
        db.session.commit()

        flash("Wiki entry was added.", "success")
        return redirect(url_for("wiki.index"))
    elif request.method == "GET":
        if current_user.is_wiki_admin():
            wsettings = WikiSetting.query.get(1)
            form.is_visible.data = wsettings.default_visible

    return render_template("wiki/create.html", form=form, nav=(prepare_wiki_nav(), WikiSearchForm()), title=page_title("Create wiki entry"))

@bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    wikientry = WikiEntry.query.filter_by(id=id).first_or_404()

    form = WikiEntryForm()

    if not current_user.has_admin_role() and current_user.has_wiki_role() and wikientry.is_visible == False and wikientry.created_by.has_admin_role():
        flash_no_permission()
        return redirect(url_for(no_perm))

    if not current_user.is_wiki_admin() and wikientry.is_visible == False and not wikientry.created_by == current_user:
        flash_no_permission()
        return redirect(url_for(no_perm))

    if not current_user.is_wiki_admin():
        del form.is_visible

    if not current_user.has_admin_role():
        del form.dm_content

    if form.validate_on_submit():
        wikientry.title = form.title.data
        wikientry.content = form.content.data
        wikientry.category = form.category.data
        wikientry.tags = form.tags.data

        if current_user.is_wiki_admin():
            wikientry.is_visible = form.is_visible.data

        if current_user.has_admin_role():
            wikientry.dm_content = form.dm_content.data

        wikientry.edited_by = current_user
        wikientry.edited = datetime.utcnow()

        db.session.commit()
        flash("Wiki entry was edited.", "success")

        return redirect(url_for("wiki.index"))
    elif request.method == "GET":
        form.title.data = wikientry.title
        form.content.data = wikientry.content
        form.category.data = wikientry.category
        form.tags.data = wikientry.tags

        if current_user.is_wiki_admin():
            form.is_visible.data = wikientry.is_visible

        if current_user.has_admin_role():
            form.dm_content.data = wikientry.dm_content

    return render_template("wiki/edit.html", form=form, nav=(prepare_wiki_nav(), WikiSearchForm()), entry=wikientry, title=page_title("Edit wiki entry"))

@bp.route("/view/<int:id>", methods=["GET"])
@login_required
def view(id):
    wikientry = WikiEntry.query.filter_by(id=id).first_or_404()

    if not current_user.is_wiki_admin() and wikientry.is_visible == False and not wikientry.created_by == current_user:
        flash_no_permission()
        return redirect(url_for(no_perm))

    if not current_user.has_admin_role() and current_user.has_wiki_role() and wikientry.is_visible == False and wikientry.created_by.has_admin_role():
        flash_no_permission()
        return redirect(url_for(no_perm))

    return render_template("wiki/view.html", entry=wikientry, nav=(prepare_wiki_nav(), WikiSearchForm()), title=page_title("View wiki entry"))

@bp.route("/search/<string:text>", methods=["GET"])
@login_required
def search_text(text):
    results = search_wiki_text(text)
    results = prepare_search_result(text, results)

    return render_template("wiki/search_text.html", nav=(prepare_wiki_nav(), WikiSearchForm()), results=results, term=text, title=page_title("Search for tag"))

@bp.route("/tag/<string:tag>", methods=["GET"])
@login_required
def search_tag(tag):
    results = search_wiki_tag(tag)

    return render_template("wiki/search_tag.html", nav=(prepare_wiki_nav(), WikiSearchForm()), results=results, tag=tag, title=page_title("Search for tag"))

@bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    deny_access = redirect_non_wiki_admins()
    if deny_access:
        return redirect(url_for('index'))

    form = WikiSettingsForm()
    settings = WikiSetting.query.get(1)

    if form.validate_on_submit():
        settings.default_visible = form.default_visible.data

        db.session.commit()

        flash("Settings have been saved.", "success")
    elif request.method == "GET":
        form.default_visible.data = settings.default_visible

    return render_template("wiki/settings.html", form=form, title=page_title("Wiki settings"))