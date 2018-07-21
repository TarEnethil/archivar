from flask import flash, redirect
from models import GeneralSetting
from flask_login import current_user

def redirect_non_admins():
    if not current_user.has_admin_role():
        flash("Operation not permitted.")
        redirect(url_for("index"))

def page_title(dynamic_part=None):
    static_part = GeneralSetting.query.get(1).title

    if dynamic_part != None:
        return static_part + " - " + dynamic_part
    else:
        return static_part  