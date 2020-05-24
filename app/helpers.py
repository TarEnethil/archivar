from app import db
from app.version import version
from enum import Enum
from flask import flash, redirect, url_for, current_app
from flask_login import current_user
from functools import wraps
from hashlib import md5
from jinja2 import Markup
from sqlalchemy import func
from wtforms.validators import ValidationError

# flash generic error message
def flash_no_permission(msg=None):
    if (msg != None):
        flash(msg, "danger")
    else:
        flash("No permission for this action.", "danger")

# flash error and return a redirect
def deny_access(url, msg=None):
    flash_no_permission(msg)
    return redirect(url_for(url))

# @admin_required decorater, use AFTER login_required
def admin_required(url="index"):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_admin():
                flash("You need to be admin to perform this action.", "danger")
                return redirect(url_for(url))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# @moderator decorater, use AFTER login_required
def moderator_required(url="index"):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_at_least_moderator():
                flash("You need to be moderator or admin to perform this action.", "danger")
                return redirect(url_for(url))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# @admin_dm_or_session_required decorator, use AFTER login_required
# url must contain 'id'-param which is assumed to be a session id
def admin_dm_or_session_required(url="index"):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from app.session.models import Session

            if not 'id' in kwargs:
                flash("@admin_or_session_required was used incorrectly, contact the administrator", "danger")
                return redirect(url_for(url))

            session = Session.query.filter_by(id=kwargs['id']).first_or_404()

            if not current_user.has_admin_role() and not current_user.is_dm_of(session.campaign) and not current_user.has_char_in_session(session):
                flash("You need to be admin or have a character in this session to perform this action.", "danger")
                return redirect(url_for(url))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# @debug_mode_required decorator, use AFTER login_required
def debug_mode_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not debug_mode():
            # TODO: add link to README / documentation on how to activate it
            flash("This endpoint is only available in debug-mode.", "danger")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    return decorated_function

# generate the page <title>
def page_title(prefix):
    if prefix == None or prefix == "":
        raise UserWarning("No title prefix provided")

    return "{} {}".format(prefix, current_app.config["PAGE_TITLE_SUFFIX"])

# stretch color code from #xxx to #xxxxxx if needed
def stretch_color(color):
    if len(color) == 4:
        return "#{0}{0}{1}{1}{2}{2}".format(color[1], color[2], color[3])
    return color

# make a COUNT(id) query for a db object
def count_rows(db_class):
    return db.session.query(func.count(db_class.id)).scalar()

# validate that a form field contains {x}, {y} and {z}
class XYZ_Validator(object):
    def __call__(self, form, field):
        if not "{x}" in field.data or not "{y}" in field.data or not "{z}" in field.data:
            raise ValidationError("The tile provider needs the arguments {x} {y} and {z}")

# validate that a form field contains a value that is <= that of another field
class LessThanOrEqual(object):
    def __init__(self, comp_value_field_name):
        self.comp_value_field_name = comp_value_field_name

    def __call__(self, form, field):
        other_field = form._fields.get(self.comp_value_field_name)

        if other_field is None:
            raise Exception('No field named {} in form'.format(self.comp_value_field_name))

        if other_field.data and field.data:
            if field.data > other_field.data:
                raise ValidationError("Value must be less than or equal to {}".format(self.comp_value_field_name))

# validate that a form field contains a value that is >= that of another field
class GreaterThanOrEqual(object):
    def __init__(self, comp_value_field_name):
        self.comp_value_field_name = comp_value_field_name

    def __call__(self, form, field):
        other_field = form._fields.get(self.comp_value_field_name)

        if other_field is None:
            raise Exception('No field named {} in form'.format(self.comp_value_field_name))

        if other_field.data and field.data:
            if field.data < other_field.data:
                raise ValidationError("Value must be greater than or equal to {}".format(self.comp_value_field_name))

# validate that a form field contains a year that is valid for a given epoch
class YearPerEpochValidator(object):
    def __init__(self, epoch_id_field_name):
        self.epoch_field = epoch_id_field_name

    def __call__(self, form, field):
        from app.calendar.models import Epoch

        epoch_id = form._fields.get(self.epoch_field).data

        ep = Epoch.query.filter_by(id=epoch_id).first()

        if ep == None:
            raise ValidationError("Unknown epoch.")

        if ep.years != 0 and (field.data < 1 or field.data > ep.years):
            raise ValidationError("Year {} is invalid for this epoch.".format(field.data))

# validate that a form field contains a valid day for a given month
class DayPerMonthValidator(object):
    def __init__(self, month_id_field_name):
        self.month_field = month_id_field_name

    def __call__(self, form, field):
        from app.calendar.models import Month
        month_id = form._fields.get(self.month_field).data

        mo = Month.query.filter_by(id=month_id).first()

        if mo == None:
            raise ValidationError("Unknown month.")

        if field.data < 1 or field.data > mo.days:
            raise ValidationError("Day is invalid for this month.".format(field.data))

# validate that a user is a DM of the campaign he wants to create a session for
class IsDMValidator(object):
    def __init__(self, campaign_field_name):
        self.campaign_field = campaign_field_name

    def __call__(self, form, field):
        from app.campaign.models import Campaign
        campaign_id = form._fields.get(self.campaign_field).data

        campaign = Campaign.query.filter_by(id=campaign_id).first()

        if campaign == None:
            raise ValidationError("Unknown campaign.")

        if not current_user.is_dm_of(campaign) and not current_user.has_admin_role():
            raise ValidationError("You are not the DM of the selected campaign.")

def load_global_quicklinks():
    from app.main.models import GeneralSetting
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

    if current_app.config["SERVE_LOCAL"] == True:
        source = "local"

    local_url = url_for('static', filename="")

    s = {
        "bootstrap": {
            "cdn": ["https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css"],
            "local": ["{}css/bootstrap.min.css".format(local_url)]
        },
        "fontawesome": {
            "cdn": [    "https://use.fontawesome.com/releases/v5.3.1/css/fontawesome.css",
                        "https://use.fontawesome.com/releases/v5.3.1/css/solid.css"],
            "local": [  "{}css/fontawesome.min.css".format(local_url),
                        "{}css/solid.min.css".format(local_url)]
        },
        "markdown-editor" : {
            "cdn" : ["https://unpkg.com/easymde/dist/easymde.min.css"],
            "local" : ["{}css/easymde.min.css".format(local_url)]
        },
        "bootstrap-select" : {
            "cdn" : ["https://cdnjs.cloudflare.com/ajax/libs/bootstrap-select/1.13.1/css/bootstrap-select.min.css"],
            "local" : ["{}css/bootstrap-select.min.css".format(local_url)]
        },
        "multi-select" : {
            "cdn" : ["https://cdnjs.cloudflare.com/ajax/libs/multi-select/0.9.12/css/multi-select.min.css"],
            "local" : ["{}css/multi-select.min.css".format(local_url)]
        },
        "leaflet" : {
            "cdn" : ["https://unpkg.com/leaflet@1.3.3/dist/leaflet.css"],
            "local" : ["{}css/leaflet.css".format(local_url)]
        },
        "bootstrap-datetimepicker" : {
            "cdn" : ["https://cdnjs.cloudflare.com/ajax/libs/tempusdominus-bootstrap-4/5.0.1/css/tempusdominus-bootstrap-4.min.css"],
            "local" : ["{}css/tempusdominus.min.css".format(local_url)]
        },
        "datatables" : {
            "cdn" : ["https://cdn.datatables.net/v/bs4/dt-1.10.20/datatables.min.css"],
            "local" : ["{}css/dataTables.bootstrap.min.css".format(local_url)]
        }
    }

    for style in styles:
        if style in s:
            for url in s[style][source]:
                out += '<link rel="stylesheet" href="{}">\n'.format(url)

    return Markup(out)

def include_js(scripts):
    source = "cdn"
    out = ""

    if current_app.config["SERVE_LOCAL"] == True:
        source = "local"

    local_url = url_for('static', filename="")

    s = {
        "bootstrap": {
            "cdn": ["https://code.jquery.com/jquery-3.4.1.slim.min.js",
                    "https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js",
                    "https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js"],
            "local": [  "{}js/jquery-3.4.1.min.js".format(local_url),
                        "{}js/popper.min.js".format(local_url),
                        "{}js/bootstrap.min.js".format(local_url)]
        },
        "markdown-editor" : {
            "cdn" : ["https://unpkg.com/easymde/dist/easymde.min.js"],
            "local" : ["{}js/easymde.min.js".format(local_url)],
            "helper": [ "{}js/helpers/media-uploader.js".format(local_url),
                        "{}js/helpers/modal-helper.js".format(local_url)]
        },
        "bootstrap-select" : {
            "cdn" : ["https://cdnjs.cloudflare.com/ajax/libs/bootstrap-select/1.13.1/js/bootstrap-select.min.js"],
            "local" : ["{}js/bootstrap-select.min.js".format(local_url)]
        },
        "multi-select" : {
            "cdn" : ["https://cdnjs.cloudflare.com/ajax/libs/multi-select/0.9.12/js/jquery.multi-select.min.js"],
            "local" : ["{}js/jquery.multi-select.min.js".format(local_url)],
            "helper" : ["{}js/helpers/multi-select.js".format(local_url)]
        },
        "leaflet" : {
            "cdn" : ["https://unpkg.com/leaflet@1.3.3/dist/leaflet.js"],
            "local" : ["{}js/leaflet.js".format(local_url)]
        },
        "bootstrap-datetimepicker" : {
            "cdn" : ["https://cdnjs.cloudflare.com/ajax/libs/tempusdominus-bootstrap-4/5.0.1/js/tempusdominus-bootstrap-4.min.js"],
            "local" : ["{}js/tempusdominus.min.js".format(local_url)]
        },
        "datatables" : {
            "cdn" : ["https://cdn.datatables.net/v/bs4/dt-1.10.20/datatables.min.js"],
            "local" : ["{}js/dataTables.bootstrap.min.js".format(local_url)],
            "helper" : ["{}js/helpers/datatables.js".format(local_url)]
        },
        "quicksearch" : {
            "cdn" : ["https://cdnjs.cloudflare.com/ajax/libs/jquery.quicksearch/2.4.0/jquery.quicksearch.min.js"],
            "local" : ["{}js/jquery.quicksearch.min.js".format(local_url)]
        }
    }

    for script in scripts:
        if script in s:
            for url in s[script][source]:
                out += '<script src="{}"></script>\n'.format(url)

            if "helper" in s[script]:
                for url in s[script]["helper"]:
                    out += '<script src="{}"></script>\n'.format(url)

    # special rules for moment.js, include first because it must be before datetimepicker
    if "moment" in scripts:
        if source == "cdn":
            moment = current_app.extensions['moment'].include_moment()
        elif source == "local":
            moment = current_app.extensions['moment'].include_moment(local_js="{}js/moment-with-locales.min.js\n".format(local_url))

        out = "{}\n{}".format(moment, out)

    return Markup(out)

def get_archivar_version():
    return version()

def urlfriendly(text):
    import unicodedata
    import re

    max_len = 20

    text = str(text)
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub('[^\w\s-]', '', text).strip().lower()
    text = re.sub('[-\s]+', '-', text)

    if len(text) > max_len:
        idx = text.find("-", max_len, len(text))

        if idx >= max_len:
            text = text[:idx]

    return text

def icon_fkt(name, text_class=""):
    return Markup('<span class="fas fa-{} {}" aria-hidden="true"></span>'.format(name, text_class))

def navbar_start(no_margin=False):
    if no_margin == False:
        return Markup('<ul class="nav nav-tabs mb-4">')

    return Markup('<ul class="nav nav-tabs">')

def navbar_end():
    return Markup("</ul>")

def link(url, text, classes=None, ids=None):
    attrs = ""

    if classes != None:
        attrs += 'class="{}"'.format(classes)

    if ids != None:
        attrs += 'id="{}"'.format(ids)

    return Markup('<a href="{}" {}>{}</a>'.format(url, attrs, text))

def button_internal(url, text, icon=None, classes=None, ids=None, swap=False, icon_text_class=""):
    if icon != None:
        icon = icon_fkt(icon, text_class=icon_text_class)
    else:
        icon = ""

    if swap == False:
        text = "{}\n{}".format(icon, text)
    else:
        text = "{}\n{}".format(text, icon)

    return link(url, text, classes, ids)

def button(url, text, icon=None, classes="btn-secondary", ids=None, swap=False, icon_text_class=""):
    return button_internal(url, text, icon, "btn {}".format(classes), ids, swap, icon_text_class=icon_text_class)

def button_nav(url, text, icon=None, classes="", ids=None, swap=False, icon_text_class="", li_classes=""):
    btn = '<li class="nav-item {}">{}</li>'.format(li_classes, button_internal(url, text, icon, "nav-link {}".format(classes), ids, swap, icon_text_class))

    return Markup(btn)

class Role(Enum):
    User = 0
    Moderator = 1
    Admin = 2

def debug_mode():
    return current_app.config["DEBUG"] == True

def register_processors_and_filters(app):
    @app.context_processor
    def utility_processor():
        return dict(load_global_quicklinks=load_global_quicklinks,
                    load_user_quicklinks=load_user_quicklinks,
                    include_css=include_css,
                    include_js=include_js,
                    get_archivar_version=get_archivar_version,
                    icon=icon_fkt,
                    navbar_start=navbar_start,
                    navbar_end=navbar_end,
                    link=link,
                    button=button,
                    button_nav=button_nav,
                    debug_mode=debug_mode)

    @app.template_filter()
    def hash(text):
        return "{}-{}".format(urlfriendly(text), md5(text.encode('utf-8')).hexdigest()[:3])

    @app.template_filter()
    def urlfriendly(text):
        from app.helpers import urlfriendly as ufriend

        return ufriend(text)