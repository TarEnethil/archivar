from config.default_config import DefaultConfig
from os import environ


class UserConfig(DefaultConfig):
    """
    User Config Class
    Uncomment a line (remove the #) to set the config variable and override the default
    Check config/README for a list of configuration options
    """

    SECRET_KEY = environ.get("SECRET_KEY") or "your_key_here"
