from flask import Blueprint

bp = Blueprint("campaign", __name__)

from app.campaign import routes
