from app import db
from app.calendar.models import CalendarSetting
from app.campaign.models import Campaign
from app.character.models import Character, Journal
from app.event.models import Event, EventSetting, EventCategory
from app.helpers import page_title, count_rows, admin_required, moderator_required, debug_mode_required, Role
from app.main import bp
from app.main.forms import LoginForm, SettingsForm, InstallForm
from app.main.models import GeneralSetting
from app.map.models import  Map, MapNode, MapSetting, MapNodeType
from app.media.models import MediaItem, MediaSetting, MediaCategory
from app.party.models import  Party
from app.session.models import Session
from app.user.models import User
from app.wiki.models import WikiSetting, WikiEntry
from collections import OrderedDict
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, send_from_directory, current_app
from flask_login import current_user, login_user, login_required, logout_user
from app.version import version
from werkzeug.urls import url_parse

@bp.before_app_request
def before_request():
    # prevent db access on static file retrieval
    if request.endpoint in ["static", "media.serve_file", "media.serve_thumbnail", "map.node_type_icon", "map.tile"]:
        return

    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

        logout_url = url_for("main.logout")
        password_url = url_for('user.password')

        allowed_urls = [logout_url, password_url]
        if current_user.must_change_password and request.path not in allowed_urls:
            flash("You must change your password before proceeding.", "warning")
            return redirect(password_url)

@bp.route("/index")
@bp.route("/")
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('main.login'))

    settings = GeneralSetting.query.get(1)
    return render_template("index.html", settings=settings, version=version(), title=page_title("Home"))

@bp.route("/about")
def about():
    return render_template("about.html", title=page_title("About Archivar"))

@bp.route("/changelog")
def changelog():
    with open(current_app.config["CHANGELOG"], "r") as markdown_file:
        changelog = markdown_file.read()

    return render_template("changelog.html", changelog=changelog, title=page_title("Changelog"))

@bp.route("/statistics")
@login_required
def statistics():
    stats = OrderedDict()

    stats["Users"] = count_rows(User)
    stats["Characters"] = count_rows(Character)
    stats["Journals"] = count_rows(Journal)
    stats["Parties"] = count_rows(Party)
    stats["Campaigns"] = count_rows(Campaign)
    stats["Sessions"] = count_rows(Session)
    stats["Maps"] = count_rows(Map)
    stats["Map Nodes"] = count_rows(MapNode)
    stats["Location Tpes"] = count_rows(MapNodeType)
    stats["Wiki articles"] = count_rows(WikiEntry)
    stats["Events"] = count_rows(Event)
    stats["Event Eategories"] = count_rows(EventCategory)
    stats["Media Files"] = count_rows(MediaItem)
    stats["Media Categories"] = count_rows(MediaCategory)

    return render_template("statistics.html", stats=stats, title=page_title("Statistics"))

@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    gset = GeneralSetting.query.get(1)
    if not gset:
        flash("You were redirected to the setup.", "info")
        return redirect(url_for("main.install"))

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
                next_page = url_for("main.index")

            return redirect(next_page)

    return render_template("login.html", title=page_title("Login"), form=form)

@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))

@bp.route("/settings", methods=["GET", "POST"])
@login_required
@moderator_required("main.index")
def settings():
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
        form.world_name.data =  settings.world_name
        form.welcome_page.data = settings.welcome_page
        form.quicklinks.data = settings.quicklinks

    return render_template("settings.html", settings=settings, form=form, title=page_title("General Settings"))

@bp.route("/__install__", methods=["GET", "POST"])
def install():
    if not GeneralSetting.query.get(1):
        form = InstallForm()

        if form.validate_on_submit():
            welcome_msg = ""

            with open(current_app.config["WELCOME_MD"], "r") as markdown_file:
                for line in markdown_file:
                    welcome_msg += line

            setting = GeneralSetting(title="My Page", welcome_page=welcome_msg)

            calendar_setting = CalendarSetting(finalized=False)
            map_setting = MapSetting(icon_anchor=0)
            wiki_setting = WikiSetting(default_visible=False)
            event_setting = EventSetting(default_visible=False)
            media_setting = MediaSetting(default_visible=False)

            event_cat = EventCategory(name="Default", color="#000000")
            media_cat = MediaCategory(name="Default")
            db.session.add(event_cat)
            db.session.add(media_cat)

            db.session.add(calendar_setting)
            db.session.add(map_setting)
            db.session.add(wiki_setting)
            db.session.add(event_setting)
            db.session.add(media_setting)

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

                flash("8 default location types were added.", "info")

            db.session.commit()

            event_setting.default_category = 1

            admin = User(username=form.admin_name.data)
            admin.set_password(form.admin_password.data)
            admin.role = Role.Admin.value
            admin.must_change_password = False

            db.session.add(admin)

            db.session.commit()

            wiki_home = WikiEntry(title="Wiki index page", content="Feel free to edit this...", dm_content="wiki entries have dm-only notes as well!", is_visible=True)
            db.session.add(wiki_home)
            db.session.commit()

            flash("Install successful. You can now log in and check the settings.", "success")

            return redirect(url_for("main.index"))

        return render_template("install.html", form=form, title="Installation")
    else:
        flash("Setup was already executed.", "danger")
        return redirect(url_for("main.index"))

@bp.route("/debuginfo", methods=["GET"])
@login_required
@debug_mode_required
def debug_info():
    import pyinfo

    pynf = pyinfo.info_as_text()

    return render_template("debuginfo.html", pynf=pynf, title=page_title("Debug Info"))

@bp.after_app_request
def debug_trace_queries(response):
    if current_app.config.get("TRACE_SQL_QUERIES"):
        from flask_sqlalchemy import get_debug_queries

        queries = get_debug_queries()
        dur = 0

        for query in queries:
            dur += query.duration

        print("processed {} queries in {}".format(len(queries), dur))

    return response

@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template("404.html", info=request.path, title="404"), 404

@bp.app_errorhandler(500)
def internal_error(error):
    return render_template("500.html", info=request.path, title="500"), 500

@bp.app_errorhandler(413)
def request_entity_too_large(error):
    size_bytes = current_app.config["MAX_CONTENT_LENGTH"]

    return render_template("413.html", size_bytes=size_bytes, title="413"), 413
