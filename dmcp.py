from app import create_app
from app.helpers import register_processors_and_filters

app = create_app()
register_processors_and_filters(app)