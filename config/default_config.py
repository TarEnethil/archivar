import os
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

"""
Default Config Class
DO NOT EDIT --- USE user_config.py INSTEAD!
"""
class DefaultConfig(object):
    # default values for user config
    MAX_CONTENT_LENGTH = 1024 * 50
    SERVE_LOCAL = True

    # static configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAPNODES_DIR = os.path.join(basedir, 'data/mapnodes/')
    MAPNODES_FILE_EXT = ["jpg", "jpeg", "png", "gif"]
    MAPTILES_DIR = os.path.join(basedir, 'data/map/')
    MEDIA_DIR = os.path.join(basedir, 'data/media/')
    WELCOME_MD = os.path.join(basedir, "Welcome.md")
    CHANGELOG = os.path.join(basedir, "CHANGELOG")