from app import db
from app.helpers import page_title, admin_required, admin_dm_or_session_required, admin_or_dm_required, urlfriendly, count_rows
from app.models import Character, Session, Campaign
from app.session import bp
from app.session.forms import SessionForm, CampaignSelectForm
from app.session.helpers import gen_participant_choices, get_session_number, get_previous_session, get_next_session
from app.campaign.helpers import gen_campaign_choices_dm, gen_campaign_choices_admin
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user

no_perm_url = "session.index"

@bp.route("/", methods=["GET"])
@login_required
def index():
    sessions_past = Session.query.filter(Session.date < datetime.utcnow()).order_by(Session.date.desc()).all()
    sessions_future = Session.query.filter(Session.date > datetime.utcnow()).order_by(Session.date.desc()).all()

    for session in sessions_future:
        session.participants.sort(key=lambda x: x.name)

    for session in sessions_past:
        session.participants.sort(key=lambda x: x.name)

    num_campaigns = count_rows(Campaign)
    url = None
    form = None

    if current_user.has_admin_role() and num_campaigns > 1:
        form = CampaignSelectForm()
        form.campaigns.choices = gen_campaign_choices_admin()
    elif current_user.is_dm_of_anything() and len(current_user.campaigns) > 1:
        form = CampaignSelectForm()
        form.campaigns.choices = gen_campaign_choices_dm()
    elif current_user.has_admin_role() and num_campaigns == 1:
        campaign = Campaign.query.first()
        url = url_for('session.create_with_campaign', id=campaign.id)
    elif current_user.is_dm_of_anything() and len(current_user.campaigns) == 1:
        url = url_for('session.create_with_campaign', id=current_user.campaigns[0].id)

    return render_template("session/list.html", sessions_past=sessions_past, sessions_future=sessions_future, form=form, url=url, title=page_title("Sessions"))

# currently just a backup, actual handling is done via in-page form (session.list)
@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if not current_user.has_admin_role() and not current_user.is_dm_of_anything():
        flash("You are now allowed to perform this action.", "danger")
        return redirect(request.referrer)

    if not current_user.has_admin_role() and len(current_user.campaigns) == 1:
        return redirect(url_for("session.create_with_campaign", id=current_user.campaigns[0].id))

    if current_user.has_admin_role() and count_rows(Campaign) == 1:
        campaign = Campaign.query.first()
        return redirect(url_for("session.create_with_campaign", id=campaign.id))

    form = CampaignSelectForm()

    if current_user.has_admin_role():
        form.campaigns.choices = gen_campaign_choices_admin()
    else:
        form.campaigns.choices = gen_campaign_choices_dm()

    if form.validate_on_submit():
        return redirect(url_for("session.create_with_campaign", id=form.campaigns.data))

    return render_template("session/choose_campaign.html", form=form, title=page_title("Choose a Campaign"))

@bp.route("/create/for-campaign/<int:id>", methods=["GET", "POST"])
@login_required
@admin_or_dm_required(no_perm_url)
def create_with_campaign(id):
    form = SessionForm()
    form.submit.label.text = "Create Session"
    form.participants.choices = gen_participant_choices()

    campaign = Campaign.query.filter_by(id=id).first_or_404()

    if not current_user.is_dm_of(campaign):
        del form.dm_notes

    if form.validate_on_submit():
        participants = Character.query.filter(Character.id.in_(form.participants.data)).all()

        dm_notes = None
        if current_user.is_dm_of(campaign):
            dm_notes = form.dm_notes.data

        new_session = Session(title=form.title.data, campaign_id=form.campaign.data, summary=form.summary.data, dm_notes=dm_notes, date=form.date.data, participants=participants)

        db.session.add(new_session)
        db.session.commit()

        flash("Session was created.", "success")
        return redirect(url_for("session.view", id=new_session.id, name=urlfriendly(new_session.title)))
    elif request.method == "GET":
        participants = []

        for p in campaign.default_participants:
            participants.append(p.id)

        form.participants.data = participants

        form.campaign.data = id

    return render_template("session/create.html", form=form, campaign=campaign, title=page_title("Add Session"))

@bp.route("/edit/<int:id>/<string:name>", methods=["GET", "POST"])
@login_required
@admin_dm_or_session_required(no_perm_url)
def edit(id, name=None):
    session = Session.query.filter_by(id=id).first_or_404()
    is_admin = current_user.has_admin_role()
    is_dm = current_user.is_dm_of(session.campaign)

    form = SessionForm()
    form.submit.label.text = "Save Session"

    if is_admin or is_dm:
        form.participants.choices = gen_participant_choices()
    else:
        del form.participants
        del form.date

    if not is_dm:
        del form.dm_notes

    del form.campaign

    if form.validate_on_submit():
        session.title = form.title.data
        session.summary = form.summary.data

        if is_admin or is_dm:
            session.date = form.date.data

            participants = Character.query.filter(Character.id.in_(form.participants.data)).all()
            session.participants = participants

        if is_dm:
            session.dm_notes = form.dm_notes.data

        db.session.commit()
        flash("Session was changed.", "success")
        return redirect(url_for("session.view", id=id, name=urlfriendly(session.title)))
    elif request.method == "GET":
        form.title.data = session.title
        form.summary.data = session.summary

        if is_admin or is_dm:
            form.date.data = session.date

            participants = []

            for p in session.participants:
                participants.append(p.id)

            form.participants.data = participants

        if is_dm:
            form.dm_notes.data = session.dm_notes

    return render_template("session/edit.html", form=form, title=page_title("Edit Session '%s'" % session.title))

@bp.route("/view/<int:id>/<string:name>", methods=["GET"])
@bp.route("/view/<int:id>", methods=["GET"])
@login_required
def view(id, name=None):
    session = Session.query.filter_by(id=id).first_or_404()
    prev_session = get_previous_session(session)
    next_session = get_next_session(session)

    session.participants.sort(key=lambda x: x.name)

    return render_template("session/view.html", session=session, prev=prev_session, next=next_session, title=page_title("View Session '%s'" % session.title))

@bp.route("/delete/<int:id>/<string:name>")
@login_required
@admin_required(no_perm_url)
def delete(id, name=None):
    session = Session.query.filter_by(id=id).first_or_404()

    db.session.delete(session)
    db.session.commit()

    flash("Session was deleted.", "success")
    return redirect(url_for("session.index"))

@bp.route("/sidebar", methods=["GET"])
@login_required
def sidebar():
    sessions = Session.query.with_entities(Session.id, Session.title).order_by(Session.date.asc()).all()

    return jsonify(sessions)