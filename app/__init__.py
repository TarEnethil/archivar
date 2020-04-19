from flask import Flask, url_for
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_bootstrap import Bootstrap, StaticCDN
from flask_moment import Moment
from flask_misaka import Misaka
from jinja2 import Markup
from sqlalchemy import MetaData
from app.version import version
import hashlib

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app, metadata=MetaData(naming_convention=naming_convention))
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
bootstrap = Bootstrap(app)
markdown = Misaka(app, tables=True, fenced_code=True, escape=True)
moment = Moment(app)

# override ConditionalCDN with StaticCDN if local serve is wanted
# reason: using the usual local cdn results in a 404 for bootstrap.min.css.map on every page
# TODO how to do this correctly?
if app.config["BOOTSTRAP_SERVE_LOCAL"]:
    app.extensions['bootstrap']['cdns']['bootstrap'] = StaticCDN(static_endpoint='static_files')
    app.extensions['bootstrap']['cdns']['jquery'] = StaticCDN(static_endpoint='static_files')

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

from app.models import GeneralSetting

@app.context_processor
def utility_processor():
    def load_global_quicklinks():
        gset = GeneralSetting.query.get(1)
        quicklinks = []

        if not gset or not gset.quicklinks:
            return quicklinks

        for line in gset.quicklinks.splitlines():
            parts = line.split("|")

            if len(parts) == 2 and len(parts[0]) > 0 and len(parts[1]) > 0:
                quicklinks.append(parts)

        return quicklinks

    def load_user_quicklinks():
        quicklinks = []

        if not current_user.quicklinks:
            return quicklinks

        for line in current_user.quicklinks.splitlines():
            parts = line.split("|")

            if len(parts) == 2 and len(parts[0]) > 0 and len(parts[1]) > 0:
                quicklinks.append(parts)

        return quicklinks

    def include_css(styles):
        source = "cdn"
        out = ""

        if app.config["BOOTSTRAP_SERVE_LOCAL"] == True:
            source = "local"

        local_url = url_for('static_files', filename="")

        s = {
            # we prevent simplemde from automatically downloading font-awesome from CDN, so we need to add URLs here
            "simplemde" : {
                "cdn" : ["https://cdn.jsdelivr.net/simplemde/latest/simplemde.min.css", "https://maxcdn.bootstrapcdn.com/font-awesome/latest/css/font-awesome.min.css"],
                "local" : [local_url + "css/simplemde.min.css", local_url + "css/font-awesome.min.css"]
            },
            "bootstrap-select" : {
                "cdn" : ["https://cdnjs.cloudflare.com/ajax/libs/bootstrap-select/1.13.1/css/bootstrap-select.min.css"],
                "local" : [local_url + "css/bootstrap-select.min.css"]
            },
            "multi-select" : {
                "cdn" : ["https://cdnjs.cloudflare.com/ajax/libs/multi-select/0.9.12/css/multi-select.min.css"],
                "local" : [local_url + "css/multi-select.min.css"]
            },
            "leaflet" : {
                "cdn" : ["https://unpkg.com/leaflet@1.3.3/dist/leaflet.css"],
                "local" : [local_url + "css/leaflet.css"]
            },
            "bootstrap-datetimepicker" : {
                "cdn" : ["https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datetimepicker/4.17.47/css/bootstrap-datetimepicker.min.css"],
                "local" : [local_url + "css/bootstrap-datetimepicker.min.css"]
            },
            "datatables" : {
                "cdn" : ["https://cdn.datatables.net/1.10.18/css/dataTables.bootstrap.min.css"],
                "local" : [local_url + "css/dataTables.bootstrap.min.css"]
            }
        }

        for style in styles:
            if style in s:
                for url in s[style][source]:
                    out += '<link rel="stylesheet" href="' + url + '">\n'

        return Markup(out)

    def include_js(scripts):
        source = "cdn"
        out = ""

        if app.config["BOOTSTRAP_SERVE_LOCAL"] == True:
            source = "local"

        local_url = url_for('static_files', filename="")

        s = {
            "simplemde" : {
                "cdn" : ["https://cdn.jsdelivr.net/simplemde/latest/simplemde.min.js"],
                "local" : [local_url + "js/simplemde.min.js"]
            },
            "bootstrap-select" : {
                "cdn" : ["https://cdnjs.cloudflare.com/ajax/libs/bootstrap-select/1.13.1/js/bootstrap-select.min.js"],
                "local" : [local_url + "js/bootstrap-select.min.js"]
            },
            "multi-select" : {
                "cdn" : ["https://cdnjs.cloudflare.com/ajax/libs/multi-select/0.9.12/js/jquery.multi-select.min.js"],
                "local" : [local_url + "js/jquery.multi-select.min.js"],
                "helper" : [local_url + "js/helpers/multi-select.js"]
            },
            "leaflet" : {
                "cdn" : ["https://unpkg.com/leaflet@1.3.3/dist/leaflet.js"],
                "local" : [local_url + "js/leaflet.js"]
            },
            "bootstrap-datetimepicker" : {
                "cdn" : ["https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datetimepicker/4.17.47/js/bootstrap-datetimepicker.min.js"],
                "local" : [local_url + "js/bootstrap-datetimepicker.min.js"]
            },
            "datatables" : {
                "cdn" : ["https://cdn.datatables.net/1.10.18/js/jquery.dataTables.min.js", "https://cdn.datatables.net/1.10.18/js/dataTables.bootstrap.min.js"],
                "local" : [local_url + "js/jquery.dataTables.min.js", local_url + "js/dataTables.bootstrap.min.js"],
                "helper" : [local_url + "js/helpers/datatables.js"]
            },
            "quicksearch" : {
                "cdn" : ["https://cdnjs.cloudflare.com/ajax/libs/jquery.quicksearch/2.4.0/jquery.quicksearch.min.js"],
                "local" : [local_url + "js/jquery.quicksearch.min.js"]
            }
        }

        for script in scripts:
            if script in s:
                for url in s[script][source]:
                    out += '<script src="' + url + '"></script>\n'

                if "helper" in s[script]:
                    for url in s[script]["helper"]:
                        out += '<script src="' + url + '"></script>\n'

        out = Markup(out)

        # special rules for moment.js, include first because it must be before datetimepicker
        if "moment" in scripts:
            if source == "cdn":
                out = app.extensions['moment'].include_moment() + "\n" + out
            elif source == "local":
                out = app.extensions['moment'].include_moment(local_js=local_url + "js/moment-with-locales.min.js") + "\n" + out

        return out

    def get_archivar_version():
        return version()

    def icon(name):
        from app.helpers import icon as icon_fkt

        return icon_fkt(name)

    return dict(load_global_quicklinks=load_global_quicklinks,
                load_user_quicklinks=load_user_quicklinks,
                include_css=include_css,
                include_js=include_js,
                get_archivar_version=get_archivar_version,
                icon=icon)

@app.template_filter()
def hash(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()[:10]

@app.template_filter()
def urlfriendly(text):
    from app.helpers import urlfriendly as ufriend

    return ufriend(text)

from app import routes, models
