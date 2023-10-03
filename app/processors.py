from app.version import version
from flask import current_app, url_for, flash
from flask_login import current_user
from hashlib import md5
from markupsafe import Markup


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


def include_css(styles, extra_attrs=None):
    source = "cdn"
    cache_suffix = ""
    out = ""

    if current_app.config["SERVE_LOCAL"] is True:
        source = "local"
        cache_suffix = f"?av={version()}"

    local_url = url_for('static', filename="")

    s = {
        "bootstrap": {
            "cdn": ["https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"],
            "local": [f"{local_url}css/bootstrap.min.css"]
        },
        "bootstrap-night": {
            "cdn": ["https://cdn.jsdelivr.net/npm/bootstrap-dark-5@1.1.3/dist/css/bootstrap-night.min.css",
                    f"{local_url}css/bootstrap-night-custom.css"],
            "local": [f"{local_url}css/bootstrap-night.min.css",
                      f"{local_url}css/bootstrap-night-custom.css"]
        },
        "fontawesome": {
            "cdn": ["https://use.fontawesome.com/releases/v5.15.4/css/fontawesome.css",
                    "https://use.fontawesome.com/releases/v5.15.4/css/solid.css"],
            "local": [f"{local_url}css/fontawesome.min.css",
                      f"{local_url}css/solid.min.css"]
        },
        "markdown-editor": {
            "cdn": ["https://unpkg.com/easymde/dist/easymde.min.css"],
            "local": [f"{local_url}css/easymde.min.css"]
        },
        "bootstrap-select": {
            "cdn": ["https://cdnjs.cloudflare.com/ajax/libs/bootstrap-select/1.14.0-beta2/css/bootstrap-select.min.css"],  # noqa: E501
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
            "cdn": ["https://cdn.datatables.net/v/bs5/dt-1.11.5/datatables.min.css"],
            "local": [f"{local_url}css/dataTables.bootstrap.min.css"]
        }
    }

    extra = ""

    if extra_attrs is not None:
        for key, val in extra_attrs.items():
            extra += f'{key}="{val}" '

    for style in styles:
        if style in s:
            for url in s[style][source]:
                out += f'<link rel="stylesheet" href="{url}{cache_suffix}" {extra}>\n'
        else:
            flash(f"Unknown css-include requested: {style}", "warning")

    return Markup(out)


# TODO: Fix C901
def include_js(scripts):  # noqa: C901
    source = "cdn"
    cache_suffix = ""
    out = ""

    if current_app.config["SERVE_LOCAL"] is True:
        source = "local"
        cache_suffix = f"?av={version()}"

    local_url = url_for('static', filename="")

    s = {
        "bootstrap": {
            "cdn": ["https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"],
            "local": [f"{local_url}js/bootstrap.bundle.min.js"]
        },
        "jquery": {
            "cdn": ["https://code.jquery.com/jquery-3.5.1.min.js"],
            "local": [f"{local_url}js/jquery.min.js"]
        },
        "markdown-editor": {
            "cdn": ["https://unpkg.com/easymde/dist/easymde.min.js"],
            "local": [f"{local_url}js/easymde.min.js"],
            "helper": [f"{local_url}js/helpers/media-uploader.js",
                       f"{local_url}js/helpers/modal-helper.js"]
        },
        "bootstrap-select": {
            "cdn": ["https://cdn.jsdelivr.net/gh/farhadmammadli/bootstrap-select@main/js/bootstrap-select.min.js"],
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
            "cdn": ["https://cdn.datatables.net/v/bs5/dt-1.11.5/datatables.min.js"],
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
        },
        "moment": {  # need key to prevent warning for unknown script, but actual include is special case (see below)
            "cdn": [],
            "local": []
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
                out += f'<script src="{url}{cache_suffix}"></script>\n'

            if "helper" in s[script]:
                for url in s[script]["helper"]:
                    out += f'<script src="{url}{cache_suffix}"></script>\n'
        else:
            flash(f"Unknown javascript-include requested: {script}", "warning")

    # special rules for moment.js, include first because it must be before datetimepicker
    if "moment" in scripts:
        if source == "cdn":
            moment = current_app.extensions['moment'].include_moment()
        elif source == "local":
            loc_url = f"{local_url}js/moment-with-locales.min.js{cache_suffix}\n"
            moment = current_app.extensions['moment'].include_moment(local_js=loc_url)

        out = f"{moment}\n{out}"

    return Markup(out)


def short_hash(text):
    from app.helpers import urlfriendly
    return f"{urlfriendly(text)}-{md5(text.encode('utf-8')).hexdigest()[:3]}"


def register_processors_and_filters(app):
    @app.context_processor
    def utility_processor():
        from app.helpers import debug_mode, icon_fkt, navbar_start, navbar_end, link, button, button_nav

        return dict(load_global_quicklinks=load_global_quicklinks,
                    load_user_quicklinks=load_user_quicklinks,
                    include_css=include_css,
                    include_js=include_js,
                    get_archivar_version=version,
                    icon=icon_fkt,
                    navbar_start=navbar_start,
                    navbar_end=navbar_end,
                    link=link,
                    button=button,
                    button_nav=button_nav,
                    debug_mode=debug_mode)

    @app.template_filter()
    def hash(text):
        return short_hash(text)

    @app.template_filter()
    def urlfriendly(text):
        from app.helpers import urlfriendly as ufriend

        return ufriend(text)
