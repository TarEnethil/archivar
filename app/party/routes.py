from app import db
from app.character.models import Character
from app.helpers import page_title, admin_required, deny_access, upload_profile_picture, delete_profile_picture
from app.party import bp
from app.party.forms import PartyForm
from app.party.helpers import gen_party_members_choices
from app.party.models import Party
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
        new_party = Party(name=form.name.data, description=form.description.data, members=members)

        success = True
        if form.profile_picture.data:
            success, filename = upload_profile_picture(form.profile_picture.data)
            new_party.profile_picture = filename

        if success is False:
            flash("Error while creating party.", "error")
        else:
            db.session.add(new_party)
            db.session.commit()
            flash("Party was created.", "success")
            return redirect(new_party.view_url())

    return render_template("party/create.html", form=form, title=page_title("Add Party"))


# TODO: Fix C901
@bp.route("/edit/<int:id>/<string:name>", methods=["GET", "POST"])
@login_required
def edit(id, name=None):  # noqa: C901
    party = Party.query.filter_by(id=id).first_or_404()

    if not party.is_editable_by_user():
        return deny_access(no_perm_url)

    is_admin = current_user.is_admin()

    form = PartyForm()
    form.submit.label.text = "Save Party"

    if is_admin:
        form.members.choices = gen_party_members_choices(ensure=party.members)
    else:
        del form.members

    if form.validate_on_submit():
        party.name = form.name.data
        party.description = form.description.data

        if is_admin:
            members = Character.query.filter(Character.id.in_(form.members.data)).all()
            party.members = members

        success = True
        if form.profile_picture.data:
            success, filename = upload_profile_picture(form.profile_picture.data)

            if success and party.profile_picture:
                delete_profile_picture(party.profile_picture)

            party.profile_picture = filename

        if success is False:
            flash("Error while editing party.", "error")
        else:
            db.session.commit()
            flash("Party was edited.", "success")

        return redirect(party.view_url())
    elif request.method == "GET":
        form.name.data = party.name
        form.description.data = party.description

        if is_admin:
            members = []

            for m in party.members:
                members.append(m.id)

            form.members.data = members

    return render_template("party/edit.html", form=form, party=party,
                           title=page_title("Edit Party '{}'".format(party.name)))


@bp.route("/view/<int:id>/<string:name>", methods=["GET"])
@bp.route("/view/<int:id>", methods=["GET"])
@login_required
def view(id, name=None):
    party = Party.query.filter_by(id=id).first_or_404()

    return render_template("party/view.html", party=party, title=page_title("View Party '{}'".format(party.name)))


@bp.route("/delete/<int:id>/<string:name>", methods=["GET", "POST"])
@login_required
def delete(id, name=None):
    party = Party.query.filter_by(id=id).first_or_404()

    if not party.is_deletable_by_user():
        return deny_access(no_perm_url)

    db.session.delete(party)
    db.session.commit()

    flash("Party was deleted", "success")

    return redirect(url_for("character.list"))


@bp.route("/sidebar", methods=["GET"])
@login_required
def sidebar():
    party = Party.query.with_entities(Party.id, Party.name).order_by(Party.name.asc()).all()

    return jsonify(party)
