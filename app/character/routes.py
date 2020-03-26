from app import db
from app.character import bp
from app.character.forms import CreateCharacterForm, EditCharacterForm, JournalForm
from app.character.helpers import gen_session_choices
from app.helpers import page_title, flash_no_permission
from app.models import Character, Party, Journal
from datetime import datetime
from flask import render_template, flash, redirect, url_for, jsonify, request
from flask_login import current_user, login_required

no_perm = "index"

@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = CreateCharacterForm()

    if form.validate_on_submit():
        char = Character(name=form.name.data, race=form.race.data, class_=form.class_.data, description=form.description.data, private_notes=form.private_notes.data, user_id=current_user.id)

        db.session.add(char)
        db.session.commit()
        flash("Character was created.", "success")

        return redirect(url_for("character.view", id=char.id))
    else:
        return render_template("character/create.html", form=form, title=page_title("Add Character"))

@bp.route("/view/<int:id>", methods=["GET"])
@login_required
def view(id):
    char = Character.query.filter_by(id=id).first_or_404()

    return render_template("character/view.html", char=char, title=page_title("View Character '%s'" % char.name))

@bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    char = Character.query.filter_by(id=id).first_or_404()

    if current_user.id != char.user_id and current_user.has_admin_role() == False:
        flash_no_permission()
        return redirect(url_for(no_perm))

    form = EditCharacterForm()

    if not current_user.has_admin_role():
        del form.dm_notes

    if form.validate_on_submit():
        char.name = form.name.data
        char.race = form.race.data
        char.class_ = form.class_.data
        char.description = form.description.data
        char.private_notes = form.private_notes.data
        char.edited = datetime.utcnow()

        if current_user.has_admin_role():
            char.dm_notes = form.dm_notes.data

        db.session.commit()
        flash("Character changes have been saved.", "success")
        return redirect(url_for("character.view", id=id))
    else:
        form.name.data = char.name
        form.race.data = char.race
        form.class_.data = char.class_
        form.description.data = char.description
        form.private_notes.data = char.private_notes

        if current_user.has_admin_role():
            form.dm_notes.data = char.dm_notes

        return render_template("character/edit.html", form=form, title=page_title("Edit character '%s'" % char.name))

@bp.route("/list", methods=["GET"])
@login_required
def list():
    chars = Character.query.all()
    parties = Party.query.all()

    return render_template("character/list.html", chars=chars, parties=parties, title=page_title("Characters and Parties"))

@bp.route("/delete/<int:id>")
@login_required
def delete(id):
    char = Character.query.filter_by(id=id).first_or_404()

    if current_user.id != char.user_id and current_user.has_admin_role() == False:
        flash_no_permission()
        return redirect(url_for(no_perm))

    player = char.player.username

    db.session.delete(char)
    db.session.commit()

    flash("Character was deleted.", "success")
    return redirect(url_for('user.profile', username=player))

@bp.route("/sidebar", methods=["GET"])
@login_required
def sidebar():
    chars = Character.query.with_entities(Character.id, Character.name).order_by(Character.name.asc()).all()

    return jsonify(chars)

@bp.route("/journal/<int:c_id>", methods=["GET"])
@login_required
def journal_list(c_id):
    char = Character.query.filter_by(id=c_id).first_or_404()

    journals = Journal.query.filter_by(character_id = c_id).all()

    return render_template("character/journal_list.html", char=char, journals=journals, title=page_title("Journals for '%s'" % char.name))

@bp.route("/journal/<int:c_id>/create", methods=["GET", "POST"])
@login_required
def journal_create(c_id):
    char = Character.query.filter_by(id=c_id).first_or_404()

    if current_user.id != char.user_id:
        flash_no_permission()
        return redirect(url_for(no_perm))

    heading = "Create Journal Entry for " + char.name

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

        return redirect(url_for("character.journal_view", c_id=c_id, j_id=journal_entry.id))
    else:
        # pre-select session if get-param was passed
        session_id = request.args.get("session")

        # will do nothing if session_id not an int or not in choices
        if session_id:
            try:
                form.session.data = int(session_id)
            except:
                pass

        return render_template("character/journal_form.html", heading=heading, form=form, title=page_title("Add Journal Entry for '%s'" % char.name))

@bp.route("/journal/<int:c_id>/edit/<int:j_id>", methods=["GET", "POST"])
@login_required
def journal_edit(c_id, j_id):
    char = Character.query.filter_by(id=c_id).first_or_404()
    journal = Journal.query.filter_by(id=j_id).first_or_404()

    # user owns character or is admin
    if not current_user.id == char.user_id and not current_user.has_admin_role():
        flash_no_permission()
        return redirect(url_for(no_perm))

    # journal belongs to character
    if journal not in char.journals:
        flash("Journal does not belong to this character.", "danger")
        return redirect(url_for(no_perm))

    heading = "Edit Journal Entry for " + char.name

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
        return redirect(url_for("character.journal_view", c_id=c_id, j_id=journal.id))
    else:
        form.title.data = journal.title
        form.is_visible.data = journal.is_visible
        form.content.data = journal.content
        form.session.data = journal.session_id

        return render_template("character/journal_form.html", heading=heading, form=form, title=page_title("Edit Journal Entry '%s'" % journal.title))

@bp.route("/journal/<int:c_id>/view/<int:j_id>", methods=["GET"])
@login_required
def journal_view(c_id, j_id):
    char = Character.query.filter_by(id=c_id).first_or_404()
    journal = Journal.query.filter_by(id=j_id).first_or_404()

    # user owns character or is admin
    if journal.is_visible == False and not current_user.id == char.user_id and not current_user.has_admin_role():
        flash_no_permission()
        return redirect(url_for(no_perm))

    # journal belongs to character
    if journal not in char.journals:
        flash("Journal does not belong to this character.", "danger")
        return redirect(url_for(no_perm))

    return render_template("character/journal_view.html", char=char, journal=journal, title=page_title("View Journal Entry '%s'" % journal.title))

@bp.route("/journal/<int:c_id>/delete/<int:j_id>", methods=["GET"])
@login_required
def journal_delete(c_id, j_id):
    char = Character.query.filter_by(id=c_id).first_or_404()
    journal = Journal.query.filter_by(id=j_id).first_or_404()

    # user owns character or is admin
    if journal.is_visible == False and not current_user.id == char.user_id and not current_user.has_admin_role():
        flash_no_permission()
        return redirect(url_for(no_perm))

    # journal belongs to character
    if journal not in char.journals:
        flash("Journal does not belong to this character.", "danger")
        return redirect(url_for(no_perm))

    db.session.delete(journal)
    db.session.commit()

    flash("Journal entry was deleted.", "success")
    return redirect(url_for('character.view', id=char.id))