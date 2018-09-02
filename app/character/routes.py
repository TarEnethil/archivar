from flask import render_template, flash, redirect, url_for, request, jsonify
from app import db
from app.character import bp
from app.helpers import page_title, redirect_non_admins
from app.character.forms import CreateCharacterForm, EditCharacterForm, EditCharacterFormAdmin
from app.models import User, Role, GeneralSetting, Character
from flask_login import current_user, login_required
from datetime import datetime

@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = CreateCharacterForm()

    if form.validate_on_submit():
        char = Character(name=form.name.data, race=form.race.data, class_=form.class_.data, description=form.description.data, user_id=current_user.id)

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
        flash("You don't have the necessary permission for that action.", "danger")
        return redirect(url_for("index"))

    if current_user.has_admin_role():
        form = EditCharacterFormAdmin()
    else:
        form = EditCharacterForm()

    if form.validate_on_submit():
        char.name = form.name.data
        char.race = form.race.data
        char.class_ = form.class_.data
        char.description = form.description.data
        char.edited = datetime.utcnow()

        if current_user.has_admin_role():
            char.dm_notes = form.dm_notes.data

        db.session.commit()
        flash("Character changes have been saved.", "success")
        return redirect(url_for("user.profile", username=current_user.username))
    else:
        form.name.data = char.name
        form.race.data = char.race
        form.class_.data = char.class_
        form.description.data = char.description

        if current_user.has_admin_role():
            form.dm_notes.data = char.dm_notes

        return render_template("character/edit.html", form=form, title=page_title("Edit character"))