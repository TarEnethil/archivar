from app import db
from app.helpers import page_title, admin_required, admin_or_party_required
from app.models import Character, Party
from app.party import bp
from app.party.forms import PartyForm
from app.party.helpers import gen_party_members_choices
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user

no_perm_url = "character.list"

@bp.route("/create", methods=["GET", "POST"])
@login_required
@admin_required(no_perm_url)
def create():
    form = PartyForm()
    form.submit.label.text = "Create Party"
    form.members.choices = gen_party_members_choices()

    if form.validate_on_submit():
        members = Character.query.filter(Character.id.in_(form.members.data)).all()

        new_party = Party(name=form.name.data, description=form.description.data, dm_notes=form.dm_notes.data, members=members)

        db.session.add(new_party)
        db.session.commit()

        flash("Party was created.", "success")
        return redirect(url_for("party.view", id=new_party.id))

    return render_template("party/create.html", form=form, title=page_title("Create party"))

@bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
@admin_or_party_required(no_perm_url)
def edit(id):
    party = Party.query.filter_by(id=id).first_or_404()
    is_admin = current_user.has_admin_role()

    form = PartyForm()
    form.submit.label.text = "Save Party"

    if is_admin:
        form.members.choices = gen_party_members_choices()
    else:
        del form.members
        del form.dm_notes

    if form.validate_on_submit():
        party.name = form.name.data
        party.description = form.description.data

        if is_admin:
            party.dm_notes = form.dm_notes.data
            members = Character.query.filter(Character.id.in_(form.members.data)).all()
            party.members = members

        db.session.commit()
        flash("Party was changed.", "success")
        return redirect(url_for("party.view", id=id))

    elif request.method == "GET":
        form.name.data = party.name
        form.description.data = party.description

        if is_admin:
            form.dm_notes.data = party.dm_notes

            members = []

            for m in party.members:
                members.append(m.id)

            form.members.data = members

    return render_template("party/edit.html", form=form, title=page_title("Edit party '%s'" % party.name))

@bp.route("/view/<int:id>", methods=["GET"])
@login_required
def view(id):
    party = Party.query.filter_by(id=id).first_or_404()

    return render_template("party/view.html", party=party, title=page_title("View party '%s'" % party.name))

@bp.route("/delete/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required(no_perm_url)
def delete(id):
    party = Party.query.filter_by(id=id).first_or_404()

    db.session.delete(party)
    db.session.commit()

    flash("Party was deleted", "success")

    return redirect(url_for("character.list"))

@bp.route("/sidebar", methods=["GET"])
@login_required
def sidebar():
    party = Party.query.with_entities(Party.id, Party.name).order_by(Party.name.asc()).all();

    return jsonify(party);