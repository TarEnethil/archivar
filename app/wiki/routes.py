from app import db
from app.helpers import page_title, flash_no_permission, urlfriendly
from app.models import WikiEntry, WikiSetting, User, Role
from app.map.helpers import get_nodes_by_wiki_id
from app.wiki import bp
from app.wiki.forms import WikiEntryForm, WikiSettingsForm, WikiSearchForm, WikiMoveCategoryForm
from app.wiki.helpers import wiki_admin_required, prepare_wiki_nav, search_wiki_tag, search_wiki_text, prepare_search_result, get_recently_created, get_recently_edited, gen_wiki_category_choices, gen_category_strings
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from sqlalchemy import and_, or_, not_

no_perm_url = "wiki.index"

@bp.route("/", methods=["GET"])
@login_required
def index():
    return redirect(url_for("wiki.view", id=1, name=urlfriendly("Main Page")))
    return redirect(url_for("wiki.view", id=1, name=urlfriendly("Main Page")))

@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = WikiEntryForm()
    form.submit.label.text = "Create Article"
    cats = gen_category_strings()

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

        entry = WikiEntry(title=form.title.data, content=form.content.data, category=form.category.data, tags=form.tags.data, is_visible=visible, dm_content=dm_content)

        db.session.add(entry)
        db.session.commit()

        flash("Wiki entry was added.", "success")
        return redirect(entry.view_url())
    elif request.method == "GET":
        if current_user.is_wiki_admin():
            wsettings = WikiSetting.query.get(1)
            form.is_visible.data = wsettings.default_visible

    return render_template("wiki/create.html", form=form, nav=(prepare_wiki_nav(), WikiSearchForm()), cats=cats, title=page_title("Add Wiki Article"))

@bp.route("/edit/<int:id>/<string:name>", methods=["GET", "POST"])
@login_required
def edit(id, name=None):
    wikientry = WikiEntry.query.filter_by(id=id).first_or_404()

    form = WikiEntryForm()
    form.submit.label.text = "Save Article"
    cats = gen_category_strings()

    if wikientry.id == 1:
        del form.title

    # TODO: write custom decorators for this?
    if not current_user.has_admin_role() and current_user.has_wiki_role() and wikientry.is_visible == False and wikientry.created_by.has_admin_role():
        flash_no_permission()
        return redirect(url_for(no_perm_url))

    if not current_user.is_wiki_admin() and wikientry.is_visible == False and not wikientry.created_by == current_user:
        flash_no_permission()
        return redirect(url_for(no_perm_url))

    if not current_user.is_wiki_admin():
        del form.is_visible

    if not current_user.has_admin_role():
        del form.dm_content

    if form.validate_on_submit():
        if wikientry.id != 1:
            wikientry.title = form.title.data

        wikientry.content = form.content.data
        wikientry.category = form.category.data
        wikientry.tags = form.tags.data

        if current_user.is_wiki_admin():
            wikientry.is_visible = form.is_visible.data

        if current_user.has_admin_role():
            wikientry.dm_content = form.dm_content.data

        db.session.commit()
        flash("Wiki entry was edited.", "success")

        return redirect(wikientry.view_url())
    elif request.method == "GET":
        if wikientry.id != 1:
            form.title.data = wikientry.title

        form.content.data = wikientry.content
        form.category.data = wikientry.category
        form.tags.data = wikientry.tags

        if current_user.is_wiki_admin():
            form.is_visible.data = wikientry.is_visible

        if current_user.has_admin_role():
            form.dm_content.data = wikientry.dm_content

    return render_template("wiki/edit.html", form=form, nav=(prepare_wiki_nav(), WikiSearchForm()), cats=cats, entry=wikientry, title=page_title("Edit Wiki Article '%s'" % wikientry.title))

@bp.route("/view/<int:id>/<string:name>", methods=["GET"])
@bp.route("/view/<int:id>", methods=["GET"])
@login_required
def view(id, name=None):
    wikientry = WikiEntry.query.filter_by(id=id).first_or_404()

    # TODO: write custom decorator / function for this?
    if not current_user.is_wiki_admin() and wikientry.is_visible == False and not wikientry.created_by == current_user:
        flash_no_permission()
        return redirect(url_for(no_perm_url))

    if not current_user.has_admin_role() and current_user.has_wiki_role() and wikientry.is_visible == False and wikientry.created_by.has_admin_role():
        flash_no_permission()
        return redirect(url_for(no_perm_url))

    map_nodes = get_nodes_by_wiki_id(id)

    return render_template("wiki/view.html", entry=wikientry, nav=(prepare_wiki_nav(), WikiSearchForm()), map_nodes=map_nodes, title=page_title("View Wiki Article '%s'" % wikientry.title))

@bp.route("/delete/<int:id>/<string:name>", methods=["GET"])
@login_required
def delete(id, name=None):
    if id == 1:
        flash("The wiki main page can't be deleted", "danger")
        return redirect(url_for('wiki.index'))

    wikientry = WikiEntry.query.filter_by(id=id).first_or_404()

    # TODO: write custom decorator / function for this
    if not current_user.is_wiki_admin() and wikientry.is_visible == False and not wikientry.created_by == current_user:
        flash_no_permission()
        return redirect(url_for(no_perm_url))

    if not current_user.has_admin_role() and current_user.has_wiki_role() and wikientry.is_visible == False and wikientry.created_by.has_admin_role():
        flash_no_permission()
        return redirect(url_for(no_perm_url))

    db.session.delete(wikientry)
    db.session.commit()

    flash("Wiki article was deleted.", "success")
    return redirect(url_for('wiki.index'))

@bp.route("/vis/<int:id>/<string:name>", methods=["GET"])
@login_required
@wiki_admin_required
def toggle_vis(id, name=None):
    wikientry = WikiEntry.query.filter_by(id=id).first_or_404()

    # TODO: write custom decorator / function for this ?
    if not current_user.has_admin_role() and current_user.has_wiki_role() and wikientry.is_visible == False and wikientry.created_by.has_admin_role():
        flash_no_permission()
        return redirect(url_for(no_perm_url))

    if wikientry.is_visible == True:
        wikientry.is_visible = False
        flash("Article was hidden.", "success")
    else:
        wikientry.is_visible = True
        flash("Article is now visible to anyone.", "success")

    db.session.commit()
    return redirect(wikientry.view_url())

@bp.route("/search/<string:text>", methods=["GET"])
@login_required
def search_text(text):
    results = search_wiki_text(text)
    results = prepare_search_result(text, results)

    return render_template("wiki/search_text.html", nav=(prepare_wiki_nav(), WikiSearchForm()), results=results, term=text, title=page_title("Search for '%s'" % text))

@bp.route("/tag/<string:tag>", methods=["GET"])
@login_required
def search_tag(tag):
    results = search_wiki_tag(tag)

    return render_template("wiki/search_tag.html", nav=(prepare_wiki_nav(), WikiSearchForm()), results=results, tag=tag, title=page_title("Search for Tag '%s'" % tag))

@bp.route("/recent", methods=["GET"])
@login_required
def recent():
    created = get_recently_created()
    edited = get_recently_edited()

    return render_template("wiki/recent.html", nav=(prepare_wiki_nav(), WikiSearchForm()), created=created, edited=edited, title=page_title("Recent changes"))

@bp.route("/settings", methods=["GET", "POST"])
@login_required
@wiki_admin_required
def settings():
    form = WikiSettingsForm()
    move_form = WikiMoveCategoryForm()
    settings = WikiSetting.query.get(1)

    move_form.old_category.choices = gen_wiki_category_choices()

    if form.validate_on_submit() and form.submit.data:
        settings.default_visible = form.default_visible.data

        db.session.commit()

        flash("Settings have been saved.", "success")
    elif move_form.validate_on_submit() and move_form.submit_move.data:
        WikiEntry.query.filter(WikiEntry.category == move_form.old_category.data).update({WikiEntry.category: move_form.new_category.data})

        db.session.commit()

        flash('Category "' + move_form.old_category.data + '" was moved to "' + move_form.new_category.data + '".', "success")

        move_form.old_category.data = ""
        move_form.new_category.data = ""
        move_form.old_category.choices = gen_wiki_category_choices()
    elif request.method == "GET":
        form.default_visible.data = settings.default_visible

    return render_template("wiki/settings.html", settings=settings, form=form, move_form=move_form, title=page_title("Wiki Settings"))

@bp.route("/sidebar", methods=["GET"])
@login_required
def sidebar():
    if current_user.has_admin_role():
        entries = WikiEntry.query
    elif current_user.has_wiki_role():
        admins = User.query.filter(User.roles.contains(Role.query.get(1)))
        admin_ids = [a.id for a in admins]
        entries = WikiEntry.query.filter(not_(and_(WikiEntry.is_visible == False, WikiEntry.created_by_id.in_(admin_ids))))
    else:
        entries = WikiEntry.query.filter(or_(WikiEntry.is_visible == True, WikiEntry.created_by_id == current_user.id))

    entries = entries.with_entities(WikiEntry.id, WikiEntry.title, WikiEntry.is_visible).order_by(WikiEntry.title.asc()).all()

    return jsonify(entries)