from app import db
from app.mixins import SimpleChangeTracker

class GeneralSetting(db.Model, SimpleChangeTracker):
    __tablename__ = "general_settings"
    id = db.Column(db.Integer, primary_key=True)
    world_name = db.Column(db.String(64))
    welcome_page = db.Column(db.Text)
    quicklinks = db.Column(db.Text)