from flask import render_template, flash, redirect, url_for, request, jsonify
from app import db
from app.character import bp
from app.helpers import page_title, redirect_non_admins, gen_party_members_choices, flash_no_permission
from app.character.forms import CreateCharacterForm, EditCharacterForm, EditCharacterFormAdmin, PartyForm
from app.models import User, Role, GeneralSetting, Character, Party
from flask_login import current_user, login_required
from datetime import datetime

no_perm = "index"

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
        flash_no_permission()
        return redirect(url_for(no_perm))

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

@bp.route("/list", methods=["GET"])
@login_required
def list():
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    chars = Character.query.all()
    parties = Party.query.all()

    return render_template("character/list.html", chars=chars, parties=parties, title=page_title("Characters and parties"))

@bp.route("/party/create", methods=["GET", "POST"])
@login_required
def party_create():
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    form = PartyForm()
    form.members.choices = gen_party_members_choices()

    if form.validate_on_submit():
        members = Character.query.filter(Character.id.in_(form.members.data)).all()

        new_party = Party(name=form.name.data, description=form.description.data, members=members)

        db.session.add(new_party)
        db.session.commit()

        flash("Party was created.", "success")
        return redirect(url_for("character.list"))

    return render_template("character/party_create.html", form=form, title=page_title("Create party"))

@bp.route("/party/edit/<int:id>", methods=["GET", "POST"])
@login_required
def party_edit(id):
    deny_access = redirect_non_admins()
    if deny_access:
        flash_no_permission()
        return redirect(url_for(no_perm))

    party = Party.query.filter_by(id=id).first_or_404()

    form = PartyForm()
    form.members.choices = gen_party_members_choices()

    if form.validate_on_submit():
        party.name = form.name.data
        party.description = form.description.data

        members = Character.query.filter(Character.id.in_(form.members.data)).all()
        party.members = members

        db.session.commit()
        flash("Party was changed.", "success")
        return redirect(url_for("character.list"))

    elif request.method == "GET":
        form.name.data = party.name
        form.description.data = party.description

        members = []

        for m in party.members:
            members.append(m.id)

        form.members.data = members

    return render_template("character/party_edit.html", form=form, title=page_title("Edit party"))

@bp.route("/party/<int:id>", methods=["GET"])
@login_required
def party_view(id):
    party = Party.query.filter_by(id=id).first_or_404()

    return render_template("character/party_view.html", party=party, title=page_title("View party"))