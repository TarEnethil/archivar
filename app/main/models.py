from app import db
from app.user.models import SimpleAuditMixin

class GeneralSetting(db.Model, SimpleAuditMixin):
    __tablename__ = "general_settings"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    world_name = db.Column(db.String(64))
    welcome_page = db.Column(db.Text)
    quicklinks = db.Column(db.Text)