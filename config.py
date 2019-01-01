import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    ##### static configuration, editing is NOT recommended
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_DIR = os.path.join(basedir, 'static_files/')
    MAPNODES_DIR = os.path.join(basedir, 'data/mapnodes/')
    MAPNODES_FILE_EXT = ["jpg", "png", "gif"]
    MAPTILES_DIR = os.path.join(basedir, 'data/map/')
    MEDIA_DIR = os.path.join(basedir, 'data/media/')
    WELCOME_MD = os.path.join(basedir, "Welcome.md")

    ##### app configuration, can be edited
    # Key used for several cryptographic operations
    SECRET_KEY = os.environ.get("SECRET_KEY") or "bananasalad"

    # Maximum size of uploaded media (Bytes)
    MAX_CONTENT_LENGTH = 1024 * 20

    # True: Use local js and css files, False: use CDNs
    # used for ALL external css/js, not just boostrap
    BOOTSTRAP_SERVE_LOCAL = True