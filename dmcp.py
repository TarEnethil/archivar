from app import create_app
from app.processors import register_processors_and_filters
from os import environ

if environ.get("FLASK_ENV") == "development":
    from config.debug_config import DebugConfig
    app = create_app(DebugConfig)
else:
    app = create_app()

register_processors_and_filters(app)
