from app import db
from app.helpers import page_title, urlfriendly, deny_access, moderator_required
from app.map.helpers import get_nodes_by_wiki_id
from app.wiki import bp
from app.wiki.forms import WikiEntryForm, WikiSearchForm, WikiMoveCategoryForm
from app.wiki.helpers import prepare_wiki_nav, search_wiki_tag, search_wiki_text, prepare_search_result, \
    get_recently_created, get_recently_edited, gen_wiki_category_choices, gen_category_strings
from app.wiki.models import WikiEntry, WikiSetting
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required

no_perm_url = "wiki.index"


@bp.route("/", methods=["GET"])
@login_required
def index():
    return redirect(url_for("wiki.view", id=1, name=urlfriendly("Main Page")))


@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = WikiEntryForm()
    form.submit.label.text = "Create Article"
    cats = gen_category_strings()

    if form.validate_on_submit():
        entry = WikiEntry(title=form.title.data, content=form.content.data, category=form.category.data,
                          tags=form.tags.data, is_visible=form.is_visible.data)

        db.session.add(entry)
        db.session.commit()

        flash("Wiki entry was added.", "success")
        return redirect(entry.view_url())
    elif request.method == "GET":
        form.is_visible.data = True

    return render_template("wiki/create.html", form=form, nav=(prepare_wiki_nav(), WikiSearchForm()), cats=cats,
                           title=page_title("Add Wiki Article"))


@bp.route("/edit/<int:id>/<string:name>", methods=["GET", "POST"])
@login_required
def edit(id, name=None):
    wikientry = WikiEntry.query.filter_by(id=id).first_or_404()

    if not wikientry.is_editable_by_user():
        return deny_access(no_perm_url)

    form = WikiEntryForm()
    form.submit.label.text = "Save Article"
    cats = gen_category_strings()

    if wikientry.id == 1:
        del form.title

    if not wikientry.is_hideable_by_user():
        del form.is_visible

    if form.validate_on_submit():
        if wikientry.id != 1:
            wikientry.title = form.title.data

        wikientry.content = form.content.data
        wikientry.category = form.category.data
        wikientry.tags = form.tags.data

        if wikientry.is_hideable_by_user():
            wikientry.is_visible = form.is_visible.data

        db.session.commit()
        flash("Wiki entry was edited.", "success")

        return redirect(wikientry.view_url())
    elif request.method == "GET":
        if wikientry.id != 1:
            form.title.data = wikientry.title

        form.content.data = wikientry.content
        form.category.data = wikientry.category
        form.tags.data = wikientry.tags

        if wikientry.is_hideable_by_user():
            form.is_visible.data = wikientry.is_visible

    return render_template("wiki/edit.html", form=form, nav=(prepare_wiki_nav(), WikiSearchForm()), cats=cats,
                           entry=wikientry, title=page_title("Edit Wiki Article '{}'".format(wikientry.title)))


@bp.route("/view/<int:id>/<string:name>", methods=["GET"])
@bp.route("/view/<int:id>", methods=["GET"])
@login_required
def view(id, name=None):
    wikientry = WikiEntry.query.filter_by(id=id).first_or_404()

    if not wikientry.is_viewable_by_user():
        return deny_access(no_perm_url)

    if not wikientry.is_visible:
        flash("This article is only visible to you.", "warning")

    map_nodes = get_nodes_by_wiki_id(id)

    return render_template("wiki/view.html", entry=wikientry, nav=(prepare_wiki_nav(), WikiSearchForm()),
                           map_nodes=map_nodes, title=page_title("View Wiki Article '{}'".format(wikientry.title)))


@bp.route("/delete/<int:id>/<string:name>", methods=["GET"])
@login_required
def delete(id, name=None):
    if id == 1:
        flash("The wiki main page can't be deleted", "danger")
        return redirect(url_for('wiki.index'))

    wikientry = WikiEntry.query.filter_by(id=id).first_or_404()

    if not wikientry.is_deletable_by_user():
        return deny_access(no_perm_url)

    db.session.delete(wikientry)
    db.session.commit()

    flash("Wiki article was deleted.", "success")
    return redirect(url_for('wiki.index'))


@bp.route("/vis/<int:id>/<string:name>", methods=["GET"])
@login_required
def toggle_vis(id, name=None):
    wikientry = WikiEntry.query.filter_by(id=id).first_or_404()

    if not wikientry.is_hideable_by_user():
        return deny_access(no_perm_url)

    if wikientry.is_visible is True:
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

    return render_template("wiki/search_text.html", nav=(prepare_wiki_nav(), WikiSearchForm()), results=results,
                           term=text, title=page_title("Search for '{}'".format(text)))


@bp.route("/tag/<string:tag>", methods=["GET"])
@login_required
def search_tag(tag):
    results = search_wiki_tag(tag)

    return render_template("wiki/search_tag.html", nav=(prepare_wiki_nav(), WikiSearchForm()), results=results,
                           tag=tag, title=page_title("Search for Tag '{}'".format(tag)))


@bp.route("/recent", methods=["GET"])
@login_required
def recent():
    created = get_recently_created()
    edited = get_recently_edited()

    return render_template("wiki/recent.html", nav=(prepare_wiki_nav(), WikiSearchForm()), created=created,
                           edited=edited, title=page_title("Recent changes"))


@bp.route("/settings", methods=["GET", "POST"])
@login_required
@moderator_required(no_perm_url)
def settings():
    move_form = WikiMoveCategoryForm()
    settings = WikiSetting.query.get(1)

    move_form.old_category.choices = gen_wiki_category_choices()

    if move_form.validate_on_submit() and move_form.submit_move.data:
        WikiEntry.query.filter(WikiEntry.category == move_form.old_category.data) \
            .update({WikiEntry.category: move_form.new_category.data})

        db.session.commit()

        flash(f'Category "{move_form.old_category.data}" was moved to "{move_form.new_category.data}".', "success")

        move_form.old_category.data = ""
        move_form.new_category.data = ""
        move_form.old_category.choices = gen_wiki_category_choices()

    return render_template("wiki/settings.html", settings=settings, move_form=move_form,
                           title=page_title("Wiki Settings"))


@bp.route("/sidebar", methods=["GET"])
@login_required
def sidebar():
    entries = WikiEntry.get_query_for_visible_items(include_hidden_for_user=True) \
              .with_entities(WikiEntry.id, WikiEntry.title, WikiEntry.is_visible) \
              .order_by(WikiEntry.title.asc()).all()

    return jsonify(entries)
