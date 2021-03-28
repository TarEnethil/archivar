import os

# distinct data_basedir so its easier for entrypoint to manipulate
data_basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
rootdir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

dbg_intercept_redirects = False
dbg_template_editor = False
dbg_profiler_enabled = False

true_vals = ["1", "true", "yes", "y", "t"]

"""
Default Config Class
DO NOT EDIT --- USE user_config.py INSTEAD!
"""
class DefaultConfig(object):
    # static configuration
    ROOT_DIR = rootdir
    DATA_DIR = os.path.join(data_basedir, "data")
    MAPNODES_DIR = os.path.join(DATA_DIR, "mapnodes/")
    MAPTILES_DIR = os.path.join(DATA_DIR, "map/")
    MEDIA_DIR = os.path.join(DATA_DIR, "media/")
    PROFILE_PICTURE_DIR = os.path.join(DATA_DIR, "logos/")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAPNODES_FILE_EXT = ["jpg", "jpeg", "png", "gif"]
    WELCOME_MD = os.path.join(rootdir, "install", "Welcome.md")
    CHANGELOG = os.path.join(rootdir, "CHANGELOG.md")

    # default values for user config
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH") or 1024 * 1024)
    PAGE_TITLE_SUFFIX = os.environ.get("PAGE_TITLE_SUFFIX") or ":: Archivar"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or 'sqlite:///' + os.path.join(DATA_DIR, 'app.db')

    if os.environ.get("SERVE_LOCAL"):
        SERVE_LOCAL = os.environ.get("SERVE_LOCAL").lower() in true_vals
    else:
        SERVE_LOCAL = True

    # default values for debug config, these only take effect with DEBUG=True
    if os.environ.get("ENABLE_TOOLBAR"):
        ENABLE_TOOLBAR = os.environ.get("ENABLE_TOOLBAR").lower() in true_vals
    else:
        ENABLE_TOOLBAR = False

    if os.environ.get("INTERCEPT_REDIRECTS"):
        dbg_intercept_redirects = os.environ.get("INTERCEPT_REDIRECTS").lower() in true_vals

    if os.environ.get("TEMPLATE_EDITOR_ENABLED"):
        dbg_template_editor = os.environ.get("TEMPLATE_EDITOR_ENABLED").lower() in true_vals

    if os.environ.get("PROFILER_ENABLED"):
        dbg_profiler_enabled = os.environ.get("PROFILER_ENABLED").lower() in true_vals

    TOOLBAR_OPTIONS = [("INTERCEPT_REDIRECTS", dbg_intercept_redirects), ("TEMPLATE_EDITOR_ENABLED", dbg_template_editor), ("PROFILER_ENABLED", dbg_profiler_enabled)]

    if os.environ.get("LOG_SQL_QUERIES"):
        LOG_SQL_QUERIES = os.environ.get("LOG_SQL_QUERIES").lower() in true_vals
    else:
        LOG_SQL_QUERIES = False

    if os.environ.get("TRACE_SQL_QUERIES"):
        TRACE_SQL_QUERIES = os.environ.get("TRACE_SQL_QUERIES").lower() in true_vals
    else:
        TRACE_SQL_QUERIES = False
