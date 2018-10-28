from app import app, db
from app.forms import LoginForm, SettingsForm, InstallForm
from app.helpers import page_title, redirect_non_admins
from app.models import User, Role, GeneralSetting, MapSetting, MapNodeType, WikiSetting, WikiEntry, CalendarSetting, EventSetting, EventCategory
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, send_from_directory
from flask_login import current_user, login_user, login_required, logout_user
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
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    settings = GeneralSetting.query.get(1)
    return render_template("index.html", settings=settings, title=page_title("Home"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    gset = GeneralSetting.query.get(1)
    if not gset:
        flash("You were redirected to the setup.", "info")
        return redirect(url_for("install"))

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
    deny_access = redirect_non_admins()
    if deny_access:
        return redirect(url_for('index'))

    form = SettingsForm()
    settings = GeneralSetting.query.get(1)

    if form.validate_on_submit():
        settings.title = form.title.data
        settings.world_name = form.world_name.data
        settings.welcome_page = form.welcome_page.data
        settings.quicklinks = form.quicklinks.data

        flash("Settings changed.", "success")

        db.session.commit()
    else:
        form.title.data = settings.title
        form.world_name.data = settings.world_name
        form.welcome_page.data = settings.welcome_page
        form.quicklinks.data = settings.quicklinks

    return render_template("settings.html", form=form, title=page_title("General settings"))

@app.route("/__install__", methods=["GET", "POST"])
def install():
    if not GeneralSetting.query.get(1):
        form = InstallForm()

        if form.validate_on_submit():
            welcome_msg = ""

            with open(app.config["WELCOME_MD"], "r") as markdown_file:
                for line in markdown_file:
                    welcome_msg += line

            setting = GeneralSetting(title="My Page", welcome_page=welcome_msg)

            admin_role = Role(name="Admin", description="aka DM, can see everything and has text fields hidden from all other roles")
            map_role = Role(name="Map admin", description="has access to map settings; can see invisible nodes (if not created by an admin); can hide/unhide map nodes")
            wiki_role = Role(name="Wiki admin", description="has access to wiki settings; can see invisible articles (if not created by an admin); can hide/unhide wiki articles")
            event_role = Role(name="Event admin", description="has access to event settings; can add/edit event categories; can see invisible events (if not created by an admin); can hide/unhide events")
            special_role = Role(name="Special", description="no function as of yet")

            db.session.add(setting)
            db.session.add(admin_role)
            db.session.add(map_role)
            db.session.add(wiki_role)
            db.session.add(event_role)
            db.session.add(special_role)

            calendar_setting = CalendarSetting(finalized=False)
            map_setting = MapSetting(min_zoom=0, max_zoom=0, default_zoom=0, icon_anchor=0)
            wiki_setting = WikiSetting(default_visible=False)
            event_setting = EventSetting(default_visible=False)

            event_cat = EventCategory(name="Default", color="#000000")
            db.session.add(event_cat)

            db.session.add(calendar_setting)
            db.session.add(map_setting)
            db.session.add(wiki_setting)
            db.session.add(event_setting)

            # TODO: maybe remove the default icons as well
            if form.default_mapnodes.data:
                village = MapNodeType(name="Village", description="A small village with not more than 1000 inhabitants", icon_file="village.png", icon_height=35, icon_width=35)
                town = MapNodeType(name="Town", description="Towns usually have up to 5000 people living in them", icon_file="town.png", icon_height=35, icon_width=35)
                city = MapNodeType(name="City", description="Cities can have up to 10000 residents", icon_file="city.png", icon_height=35, icon_width=35)
                capital = MapNodeType(name="Capital", description="Capital city of a country or region", icon_file="capital.png", icon_height=35, icon_width=35)
                poi = MapNodeType(name="PoI", description="A particular point of interest", icon_file="poi.png", icon_height=35, icon_width=35)
                quest = MapNodeType(name="Quest", description="An old school quest marker", icon_file="quest.png", icon_height=35, icon_width=35)
                ruins = MapNodeType(name="Ruins", description="Forgotten and abandoned ruins", icon_file="ruins.png", icon_height=35, icon_width=35)
                note = MapNodeType(name="Note", description="For additional information", icon_file="note.png", icon_height=35, icon_width=35)

                db.session.add(village)
                db.session.add(town)
                db.session.add(city)
                db.session.add(capital)
                db.session.add(poi)
                db.session.add(quest)
                db.session.add(ruins)
                db.session.add(note)

                flash("8 default map nodes were added.", "info")

            db.session.commit()

            event_setting.default_category = 1

            admin = User(username=form.admin_name.data)
            admin.set_password(form.admin_password.data)
            admin.roles = [Role.query.get(1)]
            admin.must_change_password = False

            db.session.add(admin)

            db.session.commit()

            wiki_home = WikiEntry(title="Wiki index page", content="Feel free to edit this...", dm_content="wiki entries have dm-only notes as well!", is_visible=True, created_by_id=1, edited_by_id=1)
            db.session.add(wiki_home)
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

@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html", info=request.path, title="404"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template("500.html", info=request.path, title="500"), 500
