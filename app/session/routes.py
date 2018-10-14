from app import db
from app.helpers import page_title, redirect_non_admins
from app.models import Character, Session
from app.session import bp
from app.session.forms import SessionForm
from app.session.helpers import gen_participant_choices, get_session_number, get_previous_session_id, get_next_session_id
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required

no_perm = "session.index"

@bp.route("/", methods=["GET"])
@login_required
def index():
    sessions_past = Session.query.filter(Session.date < datetime.now()).order_by(Session.date.desc()).all()
    sessions_future = Session.query.filter(Session.date > datetime.now()).order_by(Session.date.desc()).all()

    return render_template("session/list.html", sessions_past=sessions_past, sessions_future=sessions_future, title=page_title("Sessions"))

@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    form = SessionForm()
    form.participants.choices = gen_participant_choices()

    if form.validate_on_submit():
        participants = Character.query.filter(Character.id.in_(form.participants.data)).all()

        if form.add_session_no.data:
            session_no = get_session_number(form.code.data)
            new_title = "#" + str(session_no + 1) + ": " + form.title.data
        else:
            new_title = form.title.data

        new_session = Session(title=new_title, code=form.code.data, summary=form.summary.data, dm_notes=form.dm_notes.data, date=form.date.data, participants=participants)

        db.session.add(new_session)
        db.session.commit()

        flash("Session was created.", "success")
        return redirect(url_for("session.index"))

    return render_template("session/create.html", form=form, title=page_title("Create session"))

@bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for(no_perm))

    session = Session.query.filter_by(id=id).first_or_404()

    form = SessionForm()
    form.participants.choices = gen_participant_choices()

    del form.add_session_no

    if form.validate_on_submit():
        session.title = form.title.data
        session.code = form.code.data
        session.summary = form.summary.data
        session.dm_notes = form.dm_notes.data
        session.date = form.date.data

        participants = Character.query.filter(Character.id.in_(form.participants.data)).all()
        session.participants = participants

        db.session.commit()
        flash("Session was changed.", "success")
        return redirect(url_for("session.index"))
    elif request.method == "GET":
        form.title.data = session.title
        form.code.data = session.code
        form.summary.data = session.summary
        form.dm_notes.data = session.dm_notes
        form.date.data = session.date

        participants = []

        for p in session.participants:
            participants.append(p.id)

        form.participants.data = participants

    return render_template("session/edit.html", form=form, title=page_title("Edit session"))

@bp.route("/view/<int:id>", methods=["GET"])
@login_required
def view(id):
    session = Session.query.filter_by(id=id).first_or_404()
    prev_session_id = get_previous_session_id(session.date, session.code)
    next_session_id = get_next_session_id(session.date, session.code)

    return render_template("session/view.html", session=session, prev=prev_session_id, next=next_session_id, title=page_title("View session"))

@bp.route("/sidebar", methods=["GET"])
@login_required
def sidebar():
    sessions = Session.query.with_entities(Session.id, Session.title).order_by(Session.date.asc()).all()

    return jsonify(sessions)