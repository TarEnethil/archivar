from config.user_config import UserConfig
from flask import Flask, url_for
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_misaka import Misaka
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from markupsafe import Markup
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
bootstrap = Bootstrap5()
markdown = Misaka(tables=True, fenced_code=True, escape=True, strikethrough=True)
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
    if app.config.get("DEBUG") is True:
        # enable Flask-DebugToolbar
        if app.config.get("ENABLE_TOOLBAR") is True:
            print("Enabling Flask-DebugToolbar")
            from flask_debugtoolbar import DebugToolbarExtension
            DebugToolbarExtension(app)

            for tup in app.config.get("TOOLBAR_OPTIONS"):
                print(f"Setting Flask-Toolbar option: {tup[0]} = {tup[1]}")
                app.config[f"DEBUG_TB_{tup[0]}"] = tup[1]

        # enable SQLAlchemy query logging to stderr
        if app.config.get("LOG_SQL_QUERIES") is True:
            print("Enabling SQL-logging to stderr")
            app.config["SQLALCHEMY_ECHO"] = True

        # trace the count and length of queries for each request
        if app.config.get("TRACE_SQL_QUERIES") is True:
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

    from app.random import bp as random_bp
    app.register_blueprint(random_bp, url_prefix="/random")

    return app


from app.calendar import models as calendar_models
from app.campaign import models as campaign_models
from app.character import models as character_models
from app.event import models as event_models
from app.main import models as main_models
from app.map import models as map_models
from app.media import models as media_models
from app.party import models as party_models
from app.session import models as session_models
from app.user import models as user_models
from app.wiki import models as wiki_models
