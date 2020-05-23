from app import db
from app.character import bp
from app.character.forms import CreateCharacterForm, EditCharacterForm, JournalForm
from app.character.helpers import gen_session_choices
from app.character.models import Character, Journal
from app.helpers import page_title, deny_access
from app.party.models import Party
from datetime import datetime
from flask import render_template, flash, redirect, url_for, jsonify, request
from flask_login import current_user, login_required

no_perm_url = "main.index"

@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = CreateCharacterForm()

    if form.validate_on_submit():
        char = Character(name=form.name.data, race=form.race.data, class_=form.class_.data, description=form.description.data, private_notes=form.private_notes.data, user_id=current_user.id, is_visible=form.is_visible.data)

        db.session.add(char)
        db.session.commit()
        flash("Character was created.", "success")

        return redirect(char.view_url())
    else:
        return render_template("character/create.html", form=form, title=page_title("Add Character"))

@bp.route("/view/<int:id>/<string:name>", methods=["GET"])
@bp.route("/view/<int:id>", methods=["GET"])
@login_required
def view(id, name=None):
    char = Character.query.filter_by(id=id).first_or_404()

    if not char.is_viewable_by_user():
        return deny_access(no_perm_url)

    if char.is_visible == False:
        flash("This Character is only visible to you.", "warning")

    return render_template("character/view.html", char=char, title=page_title("View Character '{}'".format(char.name)))

@bp.route("/edit/<int:id>/<string:name>", methods=["GET", "POST"])
@login_required
def edit(id, name=None):
    char = Character.query.filter_by(id=id).first_or_404()

    if not char.is_editable_by_user():
        return deny_access(no_perm_url)

    form = EditCharacterForm()

    if not char.is_owned_by_user():
        del form.private_notes

    if not char.is_hideable_by_user():
        del form.is_visible

    if form.validate_on_submit():
        char.name = form.name.data
        char.race = form.race.data
        char.class_ = form.class_.data
        char.description = form.description.data
        char.edited = datetime.utcnow()

        if char.is_owned_by_user():
            char.private_notes = form.private_notes.data

        if char.is_hideable_by_user():
            char.is_visible = form.is_visible.data

        db.session.commit()
        flash("Character changes have been saved.", "success")
        return redirect(char.view_url())
    else:
        form.name.data = char.name
        form.race.data = char.race
        form.class_.data = char.class_
        form.description.data = char.description

        if char.is_owned_by_user():
            form.private_notes.data = char.private_notes

        if char.is_hideable_by_user():
            form.is_visible.data = char.is_visible

        return render_template("character/edit.html", form=form, title=page_title("Edit character '{}'".format(char.name)))

@bp.route("/list", methods=["GET"])
@login_required
def list():
    chars = Character.get_visible_items(include_hidden_for_user=True)
    parties = Party.query.all()

    return render_template("character/list.html", chars=chars, parties=parties, title=page_title("Characters and Parties"))

@bp.route("/delete/<int:id>/<string:name>")
@login_required
def delete(id, name=None):
    char = Character.query.filter_by(id=id).first_or_404()

    if not char.is_deletable_by_user():
        return deny_access(no_perm_url)

    player = char.player

    db.session.delete(char)
    db.session.commit()

    flash("Character was deleted.", "success")
    return redirect(player.view_url())

@bp.route("/sidebar", methods=["GET"])
@login_required
def sidebar():
    chars = Character.get_query_for_visible_items(include_hidden_for_user=True).with_entities(Character.id, Character.name).order_by(Character.name.asc()).all()

    return jsonify(chars)

@bp.route("<int:c_id>/<string:c_name>/journal/", methods=["GET"])
@login_required
def journal_list(c_id, c_name=None):
    char = Character.query.filter_by(id=c_id).first_or_404()

    journals = Journal.get_query_for_visible_items(include_hidden_for_user=True).filter_by(character_id = c_id).all()

    return render_template("character/journal_list.html", char=char, journals=journals, title=page_title("Journals for '{}'".format(char.name)))

@bp.route("<int:c_id>/<string:c_name>/journal/create", methods=["GET", "POST"])
@login_required
def journal_create(c_id, c_name=None):
    char = Character.query.filter_by(id=c_id).first_or_404()

    if not char.journal_is_creatable_by_user():
        return deny_access(no_perm_url)

    heading = "Create Journal Entry for {}".format(char.name)

    form = JournalForm()
    form.session.choices = gen_session_choices(char)
    form.submit.label.text = "Create Journal Entry"

    if form.validate_on_submit():
        journal_entry = Journal(title=form.title.data, content=form.content.data, is_visible=form.is_visible.data, character_id=c_id)

        if (form.session.data != 0):
            journal_entry.session_id = form.session.data

        db.session.add(journal_entry)
        db.session.commit()
        flash("Journal entry was created.", "success")

        return redirect(journal_entry.view_url())
    else:
        # set default for visibility
        if request.method == "GET":
            form.is_visible.data = True

        # pre-select session if get-param was passed
        session_id = request.args.get("session")

        # will do nothing if session_id not an int or not in choices
        if session_id:
            try:
                form.session.data = int(session_id)
            except:
                pass

        return render_template("character/journal_form.html", heading=heading, form=form, title=page_title("Add Journal Entry for '{}'".format(char.name)))

@bp.route("<int:c_id>/<string:c_name>/journal/edit/<int:j_id>/<string:j_name>", methods=["GET", "POST"])
@login_required
def journal_edit(c_id, j_id, c_name=None, j_name=None):
    char = Character.query.filter_by(id=c_id).first_or_404()
    journal = Journal.query.filter_by(id=j_id).first_or_404()

    if not journal.is_editable_by_user():
        return deny_access(no_perm_url)

    # journal belongs to character
    if journal not in char.journals:
        return deny_access(no_perm_url, "Journal does not belong to this character.")

    heading = "Edit Journal Entry for {}".format(char.name)

    form = JournalForm()
    form.session.choices = gen_session_choices(char)
    form.submit.label.text = "Save Journal Entry"

    if form.validate_on_submit():
        journal.title = form.title.data
        journal.is_visible = form.is_visible.data
        journal.content = form.content.data

        if form.session.data == 0:
            journal.session_id = None
        else:
            journal.session_id = form.session.data

        db.session.commit()
        flash("Journal entry was changed.", "success")
        return redirect(journal.view_url())
    else:
        form.title.data = journal.title
        form.is_visible.data = journal.is_visible
        form.content.data = journal.content
        form.session.data = journal.session_id

        return render_template("character/journal_form.html", heading=heading, form=form, title=page_title("Edit Journal Entry '{}'".format(journal.title)))

@bp.route("<int:c_id>/<string:c_name>/journal/view/<int:j_id>/<string:j_name>", methods=["GET"])
@login_required
def journal_view(c_id, j_id, c_name=None, j_name=None):
    char = Character.query.filter_by(id=c_id).first_or_404()
    journal = Journal.query.filter_by(id=j_id).first_or_404()

    if not journal.is_viewable_by_user():
        return deny_access(no_perm_url)

    # journal belongs to character
    if journal not in char.journals:
        return deny_access(no_perm_url, "Journal does not belong to this character.")

    return render_template("character/journal_view.html", char=char, journal=journal, title=page_title("View Journal Entry '{}'".format(journal.title)))

@bp.route("<int:c_id>/<string:c_name>/journal/delete/<int:j_id>/<string:j_name>", methods=["GET"])
@login_required
def journal_delete(c_id, j_id, c_name=None, j_name=None):
    char = Character.query.filter_by(id=c_id).first_or_404()
    journal = Journal.query.filter_by(id=j_id).first_or_404()

    if not journal.is_deletable_by_user():
        return deny_access(no_perm_url)

    # journal belongs to character
    if journal not in char.journals:
        return deny_access(no_perm_url, "Journal does not belong to this character.")

    db.session.delete(journal)
    db.session.commit()

    flash("Journal entry was deleted.", "success")
    return redirect(char.view_url())