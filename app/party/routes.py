from flask import render_template, flash, redirect, url_for, request, jsonify
from app import db
from app.party import bp
from app.helpers import page_title, redirect_non_admins, gen_party_members_choices
from app.party.forms import PartyForm
from app.models import User, Role, GeneralSetting, Character, Party
from flask_login import current_user, login_required
from datetime import datetime

no_perm = "character.list"

@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    form = PartyForm()
    form.members.choices = gen_party_members_choices()

    if form.validate_on_submit():
        members = Character.query.filter(Character.id.in_(form.members.data)).all()

        new_party = Party(name=form.name.data, description=form.description.data, dm_notes=form.dm_notes.data, members=members)

        db.session.add(new_party)
        db.session.commit()

        flash("Party was created.", "success")
        return redirect(url_for("character.list"))

    return render_template("party/create.html", form=form, title=page_title("Create party"))

@bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    party = Party.query.filter_by(id=id).first_or_404()

    form = PartyForm()
    form.members.choices = gen_party_members_choices()

    if form.validate_on_submit():
        party.name = form.name.data
        party.description = form.description.data
        party.dm_notes = form.dm_notes.data

        members = Character.query.filter(Character.id.in_(form.members.data)).all()
        party.members = members

        db.session.commit()
        flash("Party was changed.", "success")
        return redirect(url_for("character.list"))

    elif request.method == "GET":
        form.name.data = party.name
        form.description.data = party.description
        form.dm_notes.dat = party.dm_notes

        members = []

        for m in party.members:
            members.append(m.id)

        form.members.data = members

    return render_template("party/edit.html", form=form, title=page_title("Edit party"))

@bp.route("/view/<int:id>", methods=["GET"])
@login_required
def view(id):
    party = Party.query.filter_by(id=id).first_or_404()

    return render_template("party/view.html", party=party, title=page_title("View party"))