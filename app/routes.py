from flask import render_template, flash, redirect, url_for, request, jsonify
from app import app, db
from app.forms import LoginForm, EditProfileForm
from app.models import User, Role
from flask_login import current_user, login_user, login_required, logout_user
from datetime import datetime
from werkzeug.urls import url_parse
from sqlalchemy import any_

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route("/")
@app.route("/index")
@login_required
def index():
    return render_template("index.html", title="Home")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(request.full_path)
        else:
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')

            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for("index")

            flash("Welcome, {}!".format(user.username))
            return redirect(next_page)

    return render_template("login.html", title="Login", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/user/<username>")
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()

    return render_template("user.html", user=user)

@app.route("/user/<username>/edit", methods=["GET", "POST"])
@login_required
def user_edit(username):
    if current_user.has_admin_role() or current_user.username == username:
        form = EditProfileForm()
        user = User.query.filter_by(username=username).first_or_404()

        if form.validate_on_submit():
            current_user.about = form.about.data

            if(form.password.data):
                current_user.set_password(form.password.data)

            new_user_roles = Role.query.filter(Role.id.in_(form.roles.data)).all()

            admin_role = Role.query.get(1)
        
            if username == current_user.username and current_user.has_admin_role() and admin_role not in new_user_roles:
                new_user_roles.append(admin_role)
                flash("You can't revoke your own admin role.")

            user.roles = new_user_roles

            db.session.commit()
            flash("Your changes have been saved.")

            return redirect(url_for("user", username=username))
        elif request.method == "GET":
            form.about.data = user.about

            user_roles = []
            for role in user.roles:
                user_roles.append(str(role.id))

            form.roles.data = user_roles

        return render_template("edit_profile.html", form=form, user=user)
    else:
        flash("You dont have the neccessary role to perform this action.")
        return redirect(url_for("index"))


@app.route("/test", methods=["GET", "POST"])
def test():
    if current_user.is_authenticated == True:
        x = { "eins" : "hallo", "zwei" : 2}
        return jsonify(x)
    else:
        return "no"

@app.route("/ajax")
def ajax():
    return render_template("ajax.html")