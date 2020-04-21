from flask import Flask, url_for
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_bootstrap import Bootstrap, StaticCDN
from flask_moment import Moment
from flask_misaka import Misaka
from flask_fontawesome import FontAwesome
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
fontawesome = FontAwesome()

def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)
    markdown.init_app(app)
    moment.init_app(app)
    fontawesome.init_app(app)

    # override ConditionalCDN with StaticCDN if local serve is wanted
    # reason: using the usual local cdn results in a 404 for bootstrap.min.css.map on every page
    # TODO how to do this correctly?
    if app.config["BOOTSTRAP_SERVE_LOCAL"]:
        app.extensions['bootstrap']['cdns']['bootstrap'] = StaticCDN(static_endpoint='static')
        app.extensions['bootstrap']['cdns']['jquery'] = StaticCDN(static_endpoint='static')

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

from app import models
