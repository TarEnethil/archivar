from config.user_config import UserConfig
from flask import Flask, url_for
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_misaka import Misaka
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from jinja2 import Markup
from sqlalchemy import MetaData

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))
migrate = Migrate()
login = LoginManager()
login.login_view = 'login'
bootstrap = Bootstrap()
markdown = Misaka(tables=True, fenced_code=True, escape=True)
moment = Moment()

def create_app(config=UserConfig):
    app = Flask(__name__)
    app.config.from_object(config)

    if "SECRET_KEY" not in app.config.keys() or app.config["SECRET_KEY"] in [None, "", "your_key_here"]:
        raise Exception("Invalid value for SECRET_KEY. Set a value in config/user_config.py!")

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    login.login_view = "main.login"
    bootstrap.init_app(app)
    markdown.init_app(app)
    moment.init_app(app)

    # enable debugging options if set
    if app.config.get("DEBUG") == True:
        # enable Flask-DebugToolbar
        if app.config.get("ENABLE_TOOLBAR") == True:
            print("Enabling Flask-DebugToolbar")
            from flask_debugtoolbar import DebugToolbarExtension
            toolbar = DebugToolbarExtension(app)

            for tup in app.config.get("TOOLBAR_OPTIONS"):
                print("Setting Flask-Toolbar option: {} = {}".format(tup[0], tup[1]))
                app.config["DEBUG_TB_{}".format(tup[0])] = tup[1]

        # enable SQLAlchemy query logging to stderr
        if app.config.get("LOG_SQL_QUERIES") == True:
            print("Enabling SQL-logging to stderr")
            app.config["SQLALCHEMY_ECHO"] = True

        # trace the count and length of queries for each request
        if app.config.get("TRACE_SQL_QUERIES") == True:
            print("Enabling SQL-Tracing")
            app.config["SQLALCHEMY_RECORD_QUERIES"] = True

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.user import bp as user_bp
    app.register_blueprint(user_bp, url_prefix="/user")

    from app.map import bp as map_bp
    app.register_blueprint(map_bp, url_prefix="/map")

    from app.character import bp as character_bp
    app.register_blueprint(character_bp, url_prefix="/character")

    from app.party import bp as party_bp
    app.register_blueprint(party_bp, url_prefix="/party")

    from app.session import bp as session_bp
    app.register_blueprint(session_bp, url_prefix="/session")

    from app.wiki import bp as wiki_bp
    app.register_blueprint(wiki_bp, url_prefix="/wiki")

    from app.calendar import bp as calendar_bp
    app.register_blueprint(calendar_bp, url_prefix="/calendar")

    from app.event import bp as event_bp
    app.register_blueprint(event_bp, url_prefix="/event")

    from app.media import bp as media_bp
    app.register_blueprint(media_bp, url_prefix="/media")

    from app.campaign import bp as campaign_bp
    app.register_blueprint(campaign_bp, url_prefix="/campaign")

    return app

from app.calendar import models
from app.campaign import models
from app.character import models
from app.event import models
from app.main import models
from app.map import models
from app.media import models
from app.party import models
from app.session import models
from app.user import models
from app.wiki import models