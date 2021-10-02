from flask import Blueprint

bp = Blueprint("random", __name__)

from app.random import routes
