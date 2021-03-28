from config.default_config import DefaultConfig
from os import environ

"""
User Config Class
Uncomment a line (remove the #) to set the config variable and override the default
Check config/README for a list of configuration options
"""
class UserConfig(DefaultConfig):
    SECRET_KEY = environ.get("SECRET_KEY") or "your_key_here"