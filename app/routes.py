from flask import render_template, flash, redirect, url_for, request, jsonify, send_from_directory
from app import app, db
from app.helpers import page_title, redirect_non_admins
from app.forms import LoginForm, SettingsForm, InstallForm
from app.models import User, Role, GeneralSetting, MapSetting, MapNodeType
from flask_login import current_user, login_user, login_required, logout_user
from datetime import datetime
from werkzeug.urls import url_parse

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

        url = url_for("user.edit", username=current_user.username)
        if current_user.must_change_password and request.path != url:
            flash("You must change your password before proceeding", "warning")
            return redirect(url)

@app.route("/")
@app.route("/index")
@login_required
def index():
    settings = GeneralSetting.query.get(1)
    return render_template("index.html", settings=settings, title=page_title("Home"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password", "danger")
            return redirect(request.full_path)
        else:
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')

            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for("index")

            return redirect(next_page)

    return render_template("login.html", title=page_title("Login"), form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    redirect_non_admins()

    form = SettingsForm()
    settings = GeneralSetting.query.get(1)

    if form.validate_on_submit():
        settings.title = form.title.data
        settings.world_name = form.world_name.data
        settings.welcome_page = form.welcome_page.data

        flash("Settings changed.", "success")

        db.session.commit()
    else:
        form.title.data = settings.title
        form.world_name.data = settings.world_name
        form.welcome_page.data = settings.welcome_page

    return render_template("settings.html", form=form, title=page_title("General settings"))

@app.route("/__install__", methods=["GET", "POST"])
def install():
    if not GeneralSetting.query.get(1):
        form = InstallForm()

        if form.validate_on_submit():
            setting = GeneralSetting(title="My Page", welcome_page="# Hello there!")

            admin_role = Role(name="Admin")
            map_role = Role(name="Map")
            event_role = Role(name="Event")
            special_role = Role(name="Special")

            db.session.add(setting)
            db.session.add(admin_role)
            db.session.add(map_role)
            db.session.add(event_role)
            db.session.add(special_role)

            map_setting = MapSetting(min_zoom=0, max_zoom=0, default_zoom=0, icon_anchor=0)

            db.session.add(map_setting)

            # TODO: maybe remove the default icons as well
            if form.default_mapnodes.data:
                village = MapNodeType(name="Village", description="A small village with not more than 1000 inhabitants", icon_file="village.png", icon_height=35, icon_width=35)
                town = MapNodeType(name="Town", description="Towns usually have up to 5000 people living in them", icon_file="town.png", icon_height=35, icon_width=35)
                city = MapNodeType(name="City", description="Cities can have up to 10000 residents", icon_file="city.png", icon_height=35, icon_width=35)
                capital = MapNodeType(name="Capital", description="Capital city of a country or region", icon_file="capital.png", icon_height=35, icon_width=35)
                poi = MapNodeType(name="PoI", description="A particular point of interest", icon_file="poi.png", icon_height=35, icon_width=35)
                quest = MapNodeType(name="Quest", description="An old school quest marker", icon_file="quest.png", icon_height=35, icon_width=35)
                ruins = MapNodeType(name="ruins", description="Forgotten and abandoned ruins", icon_file="ruins.png", icon_height=35, icon_width=35)
                note = MapNodeType(name="Note", description="For additional information", icon_file="note.png", icon_height=35, icon_width=35)

                db.session.add(village)
                db.session.add(town)
                db.session.add(city)
                db.session.add(capital)
                db.session.add(poi)
                db.session.add(quest)
                db.session.add(ruins)
                db.session.add(note)

                flash("7 default map nodes were added.", "info")

            db.session.commit()

            admin = User(username=form.admin_name.data)
            admin.set_password(form.admin_password.data)
            admin.roles = [Role.query.get(1)]
            admin.must_change_password = False

            db.session.add(admin)

            db.session.commit()

            flash("Install successful. You can now log in and check the settings.", "success")

            return redirect(url_for("index"))

        return render_template("install.html", form=form, title="Install")
    else:
        flash("Setup was already executed.", "danger")
        return redirect(url_for("index"))

@app.route("/static_files/<path:filename>")
def static_files(filename):
    return send_from_directory(app.config["STATIC_DIR"], filename)

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