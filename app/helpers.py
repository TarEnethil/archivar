from app import app
from flask import flash, redirect
from models import GeneralSetting
from flask_login import current_user
from werkzeug import secure_filename
import os

def redirect_non_admins():
    if not current_user.has_admin_role():
        flash("Operation not permitted.")
        redirect(url_for("index"))

def redirect_non_map_admins():
    if not current_user.is_map_admin():
        flash("Operation not permitted.")
        redirect(url_for("index"))

def page_title(dynamic_part=None):
    static_part = GeneralSetting.query.get(1).title

    if dynamic_part != None:
        return static_part + " - " + dynamic_part
    else:
        return static_part

def map_node_filename(filename_from_form):
    filename = secure_filename(filename_from_form)

    base_filename = filename

    counter = 1
    while os.path.isfile(os.path.join(app.config["MAPNODES_DIR"], base_filename)):
        split = filename.rsplit(".", 1)

        # fancy duplication avoidance (tm)
        filename = split[0] + "-" + str(counter) + "." + split[1]
        counter += 1

    return filename