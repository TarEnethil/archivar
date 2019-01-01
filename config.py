import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "bananasalad"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_DIR = os.path.join(basedir, 'static_files/')
    MAPNODES_DIR = os.path.join(basedir, 'data/mapnodes/')
    MAPNODES_FILE_EXT = ["jpg", "png", "gif"]
    MAPTILES_DIR = os.path.join(basedir, 'data/map/')
    WELCOME_MD = os.path.join(basedir, "Welcome.md")
    MEDIA_DIR = os.path.join(basedir, 'data/media/')
    MAX_CONTENT_LENGTH = 1024 * 20
    BOOTSTRAP_SERVE_LOCAL = True