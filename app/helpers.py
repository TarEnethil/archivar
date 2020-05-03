from app import db
from app.version import version
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
        flash(msg)
    else:
        flash("No permission for this action.", "danger")

# @admin_required decorater, use AFTER login_required
def admin_required(url="index"):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.has_admin_role():
                flash("You need to be admin to perform this action.", "danger")
                return redirect(url_for(url))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# @admin_or_party_required decorator, use AFTER login_required
# url must contain 'id'-param which is assumed to be a party id
def admin_or_party_required(url="index"):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from app.party.models import Party

            if not 'id' in kwargs:
                flash("@admin_or_party_required was used incorrectly, contact the administrator", "danger")
                return redirect(url_for(url))

            party = Party.query.filter_by(id=kwargs['id']).first_or_404()

            if not current_user.has_admin_role() and not current_user.has_char_in_party(party):
                flash("You need to be admin or have a character in this party to perform this action.", "danger")
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

# @admin_or_dm_required decorator, use AFTER login_required
# url must contain 'id'-param which is assumed to be a campaign id
def admin_or_dm_required(url="index"):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from app.campaign.models import Campaign

            if not 'id' in kwargs:
                flash("@admin_or_dm_required was used incorrectly, contact the administrator", "danger")
                return redirect(url_for(url))

            campaign = Campaign.query.filter_by(id=kwargs['id']).first_or_404()

            if not current_user.has_admin_role() and not current_user.is_dm_of(campaign):
                flash("You need to be admin or dm for this campaign to perform this action.", "danger")
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
def page_title(dynamic_part=None):
    from app.main.models import GeneralSetting
    gset = GeneralSetting.query.get(1)

    if not gset:
        static_part = ""
    else:
        static_part = gset.title

    if dynamic_part != None:
        return dynamic_part + " :: " + static_part
    else:
        return static_part

# stretch color code from #xxx to #xxxxxx if needed
def stretch_color(color):
    if len(color) == 4:
        return "#" + color[1] + color[1] + color[2] + color[2] + color[3] + color[3]
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
            raise Exception('No field named %s in form' % self.comp_value_field_name)

        if other_field.data and field.data:
            if field.data > other_field.data:
                raise ValidationError("Value must be less than or equal to %s" % self.comp_value_field_name)

# validate that a form field contains a value that is >= that of another field
class GreaterThanOrEqual(object):
    def __init__(self, comp_value_field_name):
        self.comp_value_field_name = comp_value_field_name

    def __call__(self, form, field):
        other_field = form._fields.get(self.comp_value_field_name)

        if other_field is None:
            raise Exception('No field named %s in form' % self.comp_value_field_name)

        if other_field.data and field.data:
            if field.data < other_field.data:
                raise ValidationError("Value must be greater than or equal to %s" % self.comp_value_field_name)

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
            raise ValidationError("Year " + field.data + " is invalid for this epoch.")

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
            raise ValidationError("Day " + field.data + " is invalid for this month.")

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
            "local": [local_url + "css/bootstrap.min.css"]
        },
        "markdown-editor" : {
            "cdn" : ["https://unpkg.com/easymde/dist/easymde.min.css"],
            "local" : [local_url + "css/easymde.min.css"]
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
            "cdn" : ["https://cdnjs.cloudflare.com/ajax/libs/tempusdominus-bootstrap-4/5.0.1/css/tempusdominus-bootstrap-4.min.css"],
            "local" : [local_url + "css/tempusdominus.min.css"]
        },
        "datatables" : {
            "cdn" : ["https://cdn.datatables.net/v/bs4/dt-1.10.20/datatables.min.css"],
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

    if current_app.config["SERVE_LOCAL"] == True:
        source = "local"

    local_url = url_for('static', filename="")

    s = {
        "bootstrap": {
            "cdn": ["https://code.jquery.com/jquery-3.4.1.slim.min.js",
                    "https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js",
                    "https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js"],
            "local": [  local_url + "js/jquery-3.4.1.min.js",
                        local_url + "js/popper.min.js",
                        local_url + "js/bootstrap.min.js"]
        },
        "markdown-editor" : {
            "cdn" : ["https://unpkg.com/easymde/dist/easymde.min.js"],
            "local" : [local_url + "js/easymde.min.js"],
            "helper": [local_url + "js/helpers/media-uploader.js"]
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
            "cdn" : ["https://cdnjs.cloudflare.com/ajax/libs/tempusdominus-bootstrap-4/5.0.1/js/tempusdominus-bootstrap-4.min.js"],
            "local" : [local_url + "js/tempusdominus.min.js"]
        },
        "datatables" : {
            "cdn" : ["https://cdn.datatables.net/v/bs4/dt-1.10.20/datatables.min.js"],
            "local" : [local_url + "js/dataTables.bootstrap.min.js"],
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
            out = current_app.extensions['moment'].include_moment() + "\n" + out
        elif source == "local":
            out = current_app.extensions['moment'].include_moment(local_js=local_url + "js/moment-with-locales.min.js") + "\n" + out

    return out

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