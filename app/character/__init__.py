from flask import Blueprint

bp = Blueprint("character", __name__)

from app.character import routes
