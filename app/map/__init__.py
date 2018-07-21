from flask import Blueprint

bp = Blueprint("map", __name__)

from app.map import routes