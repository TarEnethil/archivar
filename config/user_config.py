from config.default_config import DefaultConfig

"""
User Config Class
Uncomment a line (remove the #) to set the config variable and override the default
Check config/readme.md for a list of configuration options
"""
class UserConfig(DefaultConfig):
    SECRET_KEY = "your_key_here"