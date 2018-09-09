from app import app, db
from app.models import User, Role, MapNode, MapNodeType, WikiEntry

@app.shell_context_processor
def make_shell_context():
    return { 'db': db, 'User': User, 'Role': Role, 'MapNode': MapNode, 'WikiEntry': WikiEntry }