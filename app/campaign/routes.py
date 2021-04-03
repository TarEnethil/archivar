from app import db
from app.character.models import Character
from app.campaign import bp
from app.campaign.models import Campaign
from app.campaign.forms import CampaignCreateForm, CampaignEditForm
from app.campaign.helpers import gen_dm_choices
from app.helpers import page_title, admin_required, stretch_color, deny_access, upload_profile_picture, \
    delete_profile_picture
from app.party.helpers import gen_party_choices
from app.party.models import Party
from app.session.helpers import gen_participant_choices
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user

no_perm_url = "campaign.index"


@bp.route("/", methods=["GET"])
@login_required
def index():
    campaigns = Campaign.query.all()

    return render_template("campaign/list.html", campaigns=campaigns, title=page_title("Campaigns"))


@bp.route("/create", methods=["GET", "POST"])
@login_required
@admin_required(no_perm_url)
def create():
    form = CampaignCreateForm()
    form.dm.choices = gen_dm_choices()
    form.associated_parties.choices = gen_party_choices()
    form.default_participants.choices = gen_participant_choices()

    if form.validate_on_submit():
        associated_parties = Party.query.filter(Party.id.in_(form.associated_parties.data)).all()
        default_members = Character.query.filter(Character.id.in_(form.default_participants.data)).all()

        new_campaign = Campaign(name=form.name.data,
                                dm_id=form.dm.data,
                                description=form.description.data,
                                associated_parties=associated_parties,
                                default_participants=default_members,
                                color=stretch_color(form.color.data.hex))

        success = True
        if form.profile_picture.data:
            success, filename = upload_profile_picture(form.profile_picture.data)

            new_campaign.profile_picture = filename

        if success is False:
            flash("Error while creating campaign.", "error")
        else:
            db.session.add(new_campaign)
            db.session.commit()
            flash("Campaign was created.", "success")
            return redirect(url_for("campaign.index"))

    return render_template("campaign/create.html", form=form, title=page_title("Add Campaign"))


# TODO: Fix C901 (too complex)
@bp.route("/edit/<int:id>/<string:name>", methods=["GET", "POST"])
@login_required
def edit(id, name=None):  # noqa: C901
    campaign = Campaign.query.filter_by(id=id).first_or_404()

    if not campaign.is_editable_by_user():
        return deny_access(no_perm_url)

    is_admin = current_user.is_admin()
    is_dm = current_user.is_dm_of(campaign)

    form = CampaignEditForm()
    form.associated_parties.choices = gen_party_choices()
    form.default_participants.choices = gen_participant_choices(ensure=campaign.default_participants)

    if not is_admin:
        del form.dm
    else:
        form.dm.choices = gen_dm_choices()

    if not is_dm:
        del form.dm_notes

    if form.validate_on_submit():
        campaign.name = form.name.data
        campaign.description = form.description.data
        campaign.associated_parties = Party.query.filter(Party.id.in_(form.associated_parties.data)).all()
        campaign.default_participants = Character.query.filter(Character.id.in_(form.default_participants.data)).all()
        campaign.color = stretch_color(form.color.data.hex)

        if is_admin:
            campaign.dm_id = form.dm.data
        if is_dm:
            campaign.dm_notes = form.dm_notes.data

        success = True
        if form.profile_picture.data:
            success, filename = upload_profile_picture(form.profile_picture.data)

            if success and campaign.profile_picture:
                delete_profile_picture(campaign.profile_picture)

            campaign.profile_picture = filename

        if success is False:
            flash("Error while editing campaign.", "error")
        else:
            db.session.commit()
            flash("Campaign was edited.", "success")

        return redirect(campaign.view_url())
    elif request.method == "GET":
        form.name.data = campaign.name
        form.description.data = campaign.description
        form.color.data = campaign.color

        form.associated_parties.data = [p.id for p in campaign.associated_parties]

        participants = []
        for p in campaign.default_participants:
            participants.append(p.id)
        form.default_participants.data = participants

        if is_admin:
            form.dm.data = campaign.dm_id

        if is_dm:
            form.dm_notes.data = campaign.dm_notes

    return render_template("campaign/edit.html", form=form, campaign=campaign,
                           title=page_title("Edit Campaign '{}'".format(campaign.name)))


@bp.route("/view/<int:id>/<string:name>", methods=["GET"])
@login_required
def view(id, name=None):
    campaign = Campaign.query.filter_by(id=id).first_or_404()

    return render_template("campaign/view.html", campaign=campaign,
                           title=page_title("View Campaign '{}'".format(campaign.name)))

# @bp.route("/delete/<int:id>", methods=["GET", "POST"])
# @login_required
# @admin_required(no_perm_url)
# def delete(id):
#     party = Party.query.filter_by(id=id).first_or_404()

#     db.session.delete(party)
#     db.session.commit()

#     flash("Party was deleted", "success")

#     return redirect(url_for("character.list"))

# @bp.route("/sidebar", methods=["GET"])
# @login_required
# def sidebar():
#     party = Party.query.with_entities(Party.id, Party.name).order_by(Party.name.asc()).all();

#     return jsonify(party)
