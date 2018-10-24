from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_moment import Moment

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
bootstrap = Bootstrap(app)
moment = Moment(app)

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

from app.models import GeneralSetting

@app.context_processor
def utility_processor():
    def load_quicklinks():
        gset = GeneralSetting.query.get(1)
        quicklinks = []

        for line in gset.quicklinks.splitlines():
            print(line)
            parts = line.split("|")

            if len(parts) == 2 and len(parts[0]) > 0 and len(parts[1]) > 0:
                quicklinks.append(parts)

        return quicklinks

    return dict(load_quicklinks=load_quicklinks)

from app import routes, models