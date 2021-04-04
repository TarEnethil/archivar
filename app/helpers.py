from app import db
from app.version import version
from enum import Enum
from flask import flash, redirect, url_for, current_app
from flask_login import current_user
from functools import wraps
from hashlib import md5
from jinja2 import Markup
from os import path, remove
from PIL import Image
from sqlalchemy import func
from uuid import uuid4
from werkzeug import secure_filename
from wtforms.validators import ValidationError


# flash generic error message
def flash_no_permission(msg=None):
    if (msg is not None):
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
    if prefix is None or prefix == "":
        raise UserWarning("No title prefix provided")

    return f'{prefix} {current_app.config["PAGE_TITLE_SUFFIX"]}'


# stretch color code from #xxx to #xxxxxx if needed
def stretch_color(color):
    if len(color) == 4:
        return "#{0}{0}{1}{1}{2}{2}".format(color[1], color[2], color[3])
    return color


# make a COUNT(id) query for a db object
def count_rows(db_class):
    return db.session.query(func.count(db_class.id)).scalar()


# ensure unique and secure filename
def unique_filename(path_, initial_filename):
    orig_filename = secure_filename(initial_filename)
    filename = f"{uuid4().hex[:16]}-{orig_filename}"

    while path.isfile(path.join(path_, filename)):
        # fancy duplication avoidance (tm)
        filename = f"{uuid4().hex[:16]}-{orig_filename}"

    return filename


# generate thumbnail for an already existing image
def generate_thumbnail(path_, filename, height, width):
    filepath_orig = path.join(path_, filename)
    filepath_thumb = path.join(path_, "thumbnails", filename)

    try:
        image = Image.open(filepath_orig)
        image.thumbnail((height, width))

        image.save(filepath_thumb)
    except Exception as err:
        flash(f"Could not generate the thumbnail: {err}", "error")
        return False

    return True


# upload file to a given path
def upload_file(filedata, filepath, filename=None):
    if filename is None:
        filename = unique_filename(filepath, filedata.filename)

    try:
        filepath = path.join(filepath, filename)
        filedata.save(filepath)
    except Exception as err:
        flash(f"Could not upload file: {err}", "error")
        return False, filename

    return True, filename


# delete picture in profile dir
def delete_profile_picture(filename):
    try:
        remove(path.join(current_app.config["PROFILE_PICTURE_DIR"], filename))
    except Exception:
        flash(f"Could not delete old picture {filename}", "warning")

    try:
        remove(path.join(current_app.config["PROFILE_PICTURE_DIR"], "thumbnails", filename))
    except Exception:
        flash(f"Could not delete thumbnail of old picture {filename}", "warning")


# upload picture to profile dir
def upload_profile_picture(filedata, filename=None):
    path_ = current_app.config["PROFILE_PICTURE_DIR"]

    success, filename = upload_file(filedata, path_, filename)

    if success is False:
        return False, filename

    return generate_thumbnail(path_, filename, 100, 100), filename


# validate that a form field contains {x}, {y} and {z}
class XYZ_Validator(object):
    def __call__(self, form, field):
        if "{x}" not in field.data or "{y}" not in field.data or "{z}" not in field.data:
            raise ValidationError("The tile provider needs the arguments {x} {y} and {z}")


# validate that a form field contains a value that is <= that of another field
class LessThanOrEqual(object):
    def __init__(self, comp_value_field_name):
        self.comp_value_field_name = comp_value_field_name

    def __call__(self, form, field):
        other_field = form._fields.get(self.comp_value_field_name)

        if other_field is None:
            raise Exception(f'No field named {self.comp_value_field_name} in form')

        if other_field.data and field.data:
            if field.data > other_field.data:
                raise ValidationError(f"Value must be less than or equal to {self.comp_value_field_name}")


# validate that a form field contains a value that is >= that of another field
class GreaterThanOrEqual(object):
    def __init__(self, comp_value_field_name):
        self.comp_value_field_name = comp_value_field_name

    def __call__(self, form, field):
        other_field = form._fields.get(self.comp_value_field_name)

        if other_field is None:
            raise Exception(f'No field named {self.comp_value_field_name} in form')

        if other_field.data and field.data:
            if field.data < other_field.data:
                raise ValidationError(f"Value must be greater than or equal to {self.comp_value_field_name}")


# validate that a form field contains a year that is valid for a given epoch
class YearPerEpochValidator(object):
    def __init__(self, epoch_id_field_name):
        self.epoch_field = epoch_id_field_name

    def __call__(self, form, field):
        from app.calendar.models import Epoch

        epoch_id = form._fields.get(self.epoch_field).data

        ep = Epoch.query.filter_by(id=epoch_id).first()

        if ep is None:
            raise ValidationError("Unknown epoch.")

        if ep.years != 0 and (field.data < 1 or field.data > ep.years):
            raise ValidationError(f"Year {field.data} is invalid for this epoch.")


# validate that a form field contains a valid day for a given month
class DayPerMonthValidator(object):
    def __init__(self, month_id_field_name):
        self.month_field = month_id_field_name

    def __call__(self, form, field):
        from app.calendar.models import Month
        month_id = form._fields.get(self.month_field).data

        mo = Month.query.filter_by(id=month_id).first()

        if mo is None:
            raise ValidationError("Unknown month.")

        if field.data < 1 or field.data > mo.days:
            raise ValidationError(f"Day {field.data} is invalid for this month.")


# validate that a user is a DM of the campaign he wants to create a session for
class IsDMValidator(object):
    def __init__(self, campaign_field_name):
        self.campaign_field = campaign_field_name

    def __call__(self, form, field):
        from app.campaign.models import Campaign
        campaign_id = form._fields.get(self.campaign_field).data

        campaign = Campaign.query.filter_by(id=campaign_id).first()

        if campaign is None:
            raise ValidationError("Unknown campaign.")

        if not current_user.is_dm_of(campaign) and not current_user.is_admin():
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

    if current_app.config["SERVE_LOCAL"] is True:
        source = "local"

    local_url = url_for('static', filename="")

    s = {
        "bootstrap": {
            "cdn": ["https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css"],
            "local": [f"{local_url}css/bootstrap.min.css"]
        },
        "fontawesome": {
            "cdn": ["https://use.fontawesome.com/releases/v5.3.1/css/fontawesome.css",
                    "https://use.fontawesome.com/releases/v5.3.1/css/solid.css"],
            "local": [f"{local_url}css/fontawesome.min.css",
                      f"{local_url}css/solid.min.css"]
        },
        "markdown-editor": {
            "cdn": ["https://unpkg.com/easymde/dist/easymde.min.css"],
            "local": [f"{local_url}css/easymde.min.css"]
        },
        "bootstrap-select": {
            "cdn": ["https://cdnjs.cloudflare.com/ajax/libs/bootstrap-select/1.13.1/css/bootstrap-select.min.css"],
            "local": [f"{local_url}css/bootstrap-select.min.css"]
        },
        "multi-select": {
            "cdn": ["https://cdnjs.cloudflare.com/ajax/libs/multi-select/0.9.12/css/multi-select.min.css"],
            "local": [f"{local_url}css/multi-select.min.css"]
        },
        "leaflet": {
            "cdn": ["https://unpkg.com/leaflet@1.3.3/dist/leaflet.css"],
            "local": [f"{local_url}css/leaflet.css"]
        },
        "bootstrap-datetimepicker": {
            "cdn": ["https://cdnjs.cloudflare.com/ajax/libs/tempusdominus-bootstrap-4/5.0.1/css/tempusdominus-bootstrap-4.min.css"],  # noqa: E501
            "local": [f"{local_url}css/tempusdominus.min.css"]
        },
        "datatables": {
            "cdn": ["https://cdn.datatables.net/v/bs4/dt-1.10.20/datatables.min.css"],
            "local": [f"{local_url}css/dataTables.bootstrap.min.css"]
        }
    }

    for style in styles:
        if style in s:
            for url in s[style][source]:
                out += f'<link rel="stylesheet" href="{url}">\n'

    return Markup(out)


# TODO: Fix C901
def include_js(scripts):  # noqa: C901
    source = "cdn"
    out = ""

    if current_app.config["SERVE_LOCAL"] is True:
        source = "local"

    local_url = url_for('static', filename="")

    s = {
        "bootstrap": {
            "cdn": ["https://code.jquery.com/jquery-3.4.1.slim.min.js",
                    "https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js",
                    "https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js"],
            "local": [f"{local_url}js/jquery-3.4.1.min.js",
                      f"{local_url}js/popper.min.js",
                      f"{local_url}js/bootstrap.min.js"]
        },
        "markdown-editor": {
            "cdn": ["https://unpkg.com/easymde/dist/easymde.min.js"],
            "local": [f"{local_url}js/easymde.min.js"],
            "helper": [f"{local_url}js/helpers/media-uploader.js",
                       f"{local_url}js/helpers/modal-helper.js"]
        },
        "bootstrap-select": {
            "cdn": ["https://cdnjs.cloudflare.com/ajax/libs/bootstrap-select/1.13.1/js/bootstrap-select.min.js"],
            "local": [f"{local_url}js/bootstrap-select.min.js"]
        },
        "multi-select": {
            "cdn": ["https://cdnjs.cloudflare.com/ajax/libs/multi-select/0.9.12/js/jquery.multi-select.min.js"],
            "local": [f"{local_url}js/jquery.multi-select.min.js"],
            "helper": [f"{local_url}js/helpers/multi-select.js"]
        },
        "leaflet": {
            "cdn": ["https://unpkg.com/leaflet@1.3.3/dist/leaflet.js"],
            "local": [f"{local_url}js/leaflet.js"]
        },
        "bootstrap-datetimepicker": {
            "cdn": ["https://cdnjs.cloudflare.com/ajax/libs/tempusdominus-bootstrap-4/5.0.1/js/tempusdominus-bootstrap-4.min.js"],  # noqa: E501
            "local": [f"{local_url}js/tempusdominus.min.js"]
        },
        "datatables": {
            "cdn": ["https://cdn.datatables.net/v/bs4/dt-1.10.20/datatables.min.js"],
            "local": [f"{local_url}js/dataTables.bootstrap.min.js"],
            "helper": [f"{local_url}js/helpers/datatables.js"]
        },
        "quicksearch": {
            "cdn": ["https://cdnjs.cloudflare.com/ajax/libs/jquery.quicksearch/2.4.0/jquery.quicksearch.min.js"],
            "local": [f"{local_url}js/jquery.quicksearch.min.js"]
        },
        "bootbox": {
            "cdn": ["https://cdnjs.cloudflare.com/ajax/libs/bootbox.js/5.5.2/bootbox.min.js"],
            "local": [f"{local_url}js/bootbox.min.js"],
            "helper": [f"{local_url}js/helpers/bootbox-helper.js"]
        },
        "util": {
            "cdn": [],
            "local": [],
            "helper": [f"{local_url}js/helpers/util.js"]
        },
        "lightbox": {
            "cdn": [],
            "local": [],
            "helper": [f"{local_url}js/helpers/lightbox.js"]
        }
    }

    # TODO: better way for dependencies between scripts
    # markdown-editor includes the modals, which in turn use a confirm box
    # util uses bootbox too
    if "markdown-editor" in scripts or "util" in scripts:
        if "bootbox" not in scripts:
            scripts.append("bootbox")

    for script in scripts:
        if script in s:
            for url in s[script][source]:
                out += f'<script src="{url}"></script>\n'

            if "helper" in s[script]:
                for url in s[script]["helper"]:
                    out += f'<script src="{url}"></script>\n'

    # special rules for moment.js, include first because it must be before datetimepicker
    if "moment" in scripts:
        if source == "cdn":
            moment = current_app.extensions['moment'].include_moment()
        elif source == "local":
            loc_url = f"{local_url}js/moment-with-locales.min.js\n"
            moment = current_app.extensions['moment'].include_moment(local_js=loc_url)

        out = f"{moment}\n{out}"

    return Markup(out)


def get_archivar_version():
    return version()


def urlfriendly(text):
    import unicodedata
    import re

    max_len = 20

    text = str(text)
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    text = re.sub(r'[-\s]+', '-', text)

    if len(text) > max_len:
        idx = text.find("-", max_len, len(text))

        if idx >= max_len:
            text = text[:idx]

    return text


def icon_fkt(name, text_class=""):
    return Markup(f'<span class="fas fa-{name} {text_class}" aria-hidden="true"></span>')


def navbar_start(no_margin=False):
    if no_margin is False:
        return Markup('<ul class="nav nav-tabs mb-4">')

    return Markup('<ul class="nav nav-tabs">')


def navbar_end():
    return Markup("</ul>")


def link(url, text, classes=None, ids=None):
    attrs = ""

    if classes is not None:
        attrs += f'class="{classes}"'

    if ids is not None:
        attrs += f'id="{ids}"'

    return Markup(f'<a href="{url}" {attrs}>{text}</a>')


def button_internal(url, text, icon=None, classes=None, ids=None, swap=False, icon_text_class=""):
    if icon is not None:
        icon = icon_fkt(icon, text_class=icon_text_class)
    else:
        icon = ""

    if swap is False:
        text = f"{icon}\n{text}"
    else:
        text = f"{text}\n{icon}"

    return link(url, text, classes, ids)


def button(url, text, icon=None, classes="btn-secondary", ids=None, swap=False, icon_text_class=""):
    return button_internal(url, text, icon, f"btn {classes}", ids, swap, icon_text_class=icon_text_class)


def button_nav(url, text, icon=None, classes="", ids=None, swap=False, icon_text_class="", li_classes=""):
    inner_btn = button_internal(url, text, icon, f"nav-link {classes}", ids, swap, icon_text_class)
    btn = f'<li class="nav-item {li_classes}">{inner_btn}</li>'

    return Markup(btn)


class Role(Enum):
    User = 0
    Moderator = 1
    Admin = 2


def debug_mode():
    return current_app.config["DEBUG"] is True


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
        return f"{urlfriendly(text)}-{md5(text.encode('utf-8')).hexdigest()[:3]}"

    @app.template_filter()
    def urlfriendly(text):
        from app.helpers import urlfriendly as ufriend

        return ufriend(text)
