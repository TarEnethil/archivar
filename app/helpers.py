from app import db
from app.processors import include_css
from enum import Enum
from flask import flash, redirect, url_for, current_app
from jinja2 import Markup
from os import path, remove
from PIL import Image
from sqlalchemy import func
from uuid import uuid4
from werkzeug import secure_filename


class Role(Enum):
    User = 0
    Moderator = 1
    Admin = 2


class Theme(Enum):
    System = 0
    Light = 1
    Dark = 2

    @staticmethod
    def description(self):
        d = {
            Theme.System.value: "System Preference",
            Theme.Light.value: "Bootstrap Light",
            Theme.Dark.value: "Bootstrap Dark"
        }

        return d[self]

    @staticmethod
    def include(self):
        if self == Theme.System.value:
            out = include_css(["bootstrap-night"], {"media": "(prefers-color-scheme: dark)"})
            out += include_css(["bootstrap"], {"media": "(prefers-color-scheme: light)"})
            return out

        if self == Theme.Light.value:
            return include_css(["bootstrap"])

        if self == Theme.Dark.value:
            return include_css(["bootstrap-night"])

        raise UserWarning(f"invalid theme: {self}")


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


def debug_mode():
    return current_app.config["DEBUG"] is True


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

        if idx == -1:
            text = text[:max_len]

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
