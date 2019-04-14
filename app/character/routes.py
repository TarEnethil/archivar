from app import db
from app.character import bp
from app.character.forms import CreateCharacterForm, EditCharacterForm
from app.helpers import page_title, flash_no_permission
from app.models import Character, Party
from datetime import datetime
from flask import render_template, flash, redirect, url_for, jsonify
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

        return redirect(url_for("user.profile", username=current_user.username))
    else:
        return render_template("character/create.html", form=form, title=page_title("Create new character"))

@bp.route("/view/<int:id>", methods=["GET"])
@login_required
def view(id):
    char = Character.query.filter_by(id=id).first_or_404()

    return render_template("character/view.html", char=char, title=page_title("View character"))

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

        return render_template("character/edit.html", form=form, title=page_title("Edit character"))

@bp.route("/list", methods=["GET"])
@login_required
def list():
    chars = Character.query.all()
    parties = Party.query.all()

    return render_template("character/list.html", chars=chars, parties=parties, title=page_title("Characters and parties"))

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