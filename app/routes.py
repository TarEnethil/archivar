from flask import render_template, flash, redirect, url_for, request, jsonify
from app import app, db
from app.forms import LoginForm, CreateUserForm, EditProfileForm, EditProfileFormAdmin, SettingsForm
from app.models import User, Role, GeneralSetting
from flask_login import current_user, login_user, login_required, logout_user
from datetime import datetime
from werkzeug.urls import url_parse

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

def redirect_non_admins():
    if not current_user.has_admin_role():
        flash("Operation not permitted.")
        redirect(url_for("index"))

def page_title(dynamic_part=None):
    static_part = GeneralSetting.query.get(1).title

    if dynamic_part != None:
        return static_part + " - " + dynamic_part
    else:
        return static_part   

@app.route("/")
@app.route("/index")
@login_required
def index():
    return render_template("index.html", title=page_title("Home"))

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

    return render_template("login.html", title=page_title("Login"), form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/user/profile/<username>")
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()

    return render_template("user_profile.html", user=user, title=page_title("User profile"))

@app.route("/user/edit/<username>", methods=["GET", "POST"])
@login_required
def user_edit(username):
    if current_user.has_admin_role() or current_user.username == username:

        if current_user.has_admin_role():
            form = EditProfileFormAdmin()

            role_choices = []

            all_roles = Role.query.all()
            for role in all_roles:
                role_choices.append((str(role.id), role.name))

            form.roles.choices = role_choices
        else:
            form = EditProfileForm()

        user = User.query.filter_by(username=username).first_or_404()

        if form.validate_on_submit():
            user.about = form.about.data

            if(form.password.data):
                user.set_password(form.password.data)

            if current_user.has_admin_role():
                new_user_roles = Role.query.filter(Role.id.in_(form.roles.data)).all()

                admin_role = Role.query.get(1)
            
                if username == current_user.username and current_user.has_admin_role() and admin_role not in new_user_roles:
                    new_user_roles.append(admin_role)
                    flash("You can't revoke your own admin role.")

                user.roles = new_user_roles

            db.session.commit()
            flash("Your changes have been saved.")

            return redirect(url_for("user_profile", username=username))
        elif request.method == "GET":
            form.about.data = user.about

            if current_user.has_admin_role():
                user_roles = []
                for role in user.roles:
                    user_roles.append(str(role.id))

                form.roles.data = user_roles

        return render_template("user_edit.html", form=form, user=user, title=page_title("Edit profile"))
    else:
        flash("You dont have the neccessary role to perform this action.")
        return redirect(url_for("index"))

@app.route("/user/create", methods=["GET", "POST"])
@login_required
def user_create():
    redirect_non_admins()

    form = CreateUserForm()

    role_choices = []

    all_roles = Role.query.all()
    for role in all_roles:
        role_choices.append((str(role.id), role.name))

    form.roles.choices = role_choices

    if form.validate_on_submit():
        new_user = User(username=form.username.data)
        new_user.set_password(form.password.data)

        new_user_roles = Role.query.filter(Role.id.in_(form.roles.data)).all()
        new_user.roles = new_user_roles

        new_user.created = datetime.utcnow()

        db.session.add(new_user)
        db.session.commit()

        flash("New user " + new_user.username + " created.")
        return redirect(url_for('user_list'))
    else:
        return render_template("user_create.html", form=form, title=page_title("Create new user"))

@app.route("/user/list")
@login_required
def user_list():
    redirect_non_admins()

    users = User.query.all()

    return render_template("user_list.html", users=users, title=page_title("User list"))

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    redirect_non_admins()

    form = SettingsForm()
    settings = GeneralSetting.query.get(1)

    if form.validate_on_submit():
        settings.title = form.title.data

        flash("Settings changed.")

        db.session.commit()
    else:
        form.title.data = settings.title

    
    return render_template("settings.html", form=form, title=page_title("General settings"))

@app.route("/__install__")
def install():
    if not GeneralSetting.query.get(1):
        setting = GeneralSetting(title="My Page")

        admin_role = Role(name="Admin")
        map_role = Role(name="Map")
        event_role = Role(name="Event")
        special_role = Role(name="Special")

        db.session.add(setting)
        db.session.add(admin_role)
        db.session.add(map_role)
        db.session.add(event_role)
        db.session.add(special_role)

        db.session.commit()

        admin = User(username="Tar")
        admin.set_password("1234")
        admin.roles = [Role.query.get(1)]

        db.session.add(admin)

        db.session.commit()

        flash("Install successful")

        return redirect(url_for("index"))
    else:
        flash("Setup was already executed.")
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