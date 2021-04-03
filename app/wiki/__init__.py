from flask import Blueprint

bp = Blueprint("wiki", __name__)

from app.wiki import routes
