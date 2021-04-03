from flask import Blueprint

bp = Blueprint("party", __name__)

from app.party import routes
