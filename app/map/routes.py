from flask import render_template, flash, redirect, url_for, request, jsonify
from app import db
from app.map import bp
from app.helpers import page_title, redirect_non_admins, redirect_non_map_admins
#from app.map.forms import 
from app.models import User, Role, GeneralSetting
from flask_login import current_user, login_required

@bp.route("/")
@login_required
def index():
    return render_template("index.html")

@bp.route("/settings")
@login_required
def settings():
    return render_template("index.html")