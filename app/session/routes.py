from flask import render_template, flash, redirect, url_for, request, jsonify
from app import db
from app.session import bp
from app.helpers import page_title, redirect_non_admins, gen_participant_choices, get_session_number
from app.session.forms import SessionForm
from app.models import User, Role, GeneralSetting, Character, Party, Session
from flask_login import current_user, login_required
from datetime import datetime

@bp.route("/", methods=["GET"])
@login_required
def index():
    sessions_past = Session.query.filter(Session.date < datetime.now()).order_by(Session.date.desc()).all()
    sessions_future = Session.query.filter(Session.date > datetime.now()).order_by(Session.date.desc()).all()

    return render_template("session/list.html", sessions_past=sessions_past, sessions_future=sessions_future, title=page_title("Sessions"))

@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    redirect_non_admins()

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
        return redirect(url_for("sessin.index"))

    return render_template("session/create.html", form=form, title=page_title("Create session"))

@bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    redirect_non_admins()

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

    return render_template("session/view.html", session=session, title=page_title("View session"))