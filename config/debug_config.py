from config.user_config import UserConfig

"""
Debug Config Class
inherits from UserConfig, because we want to run debug mode with the user's configuration + debug options
"""
class DebugConfig(UserConfig):
    SECRET_KEY = "debugging4lyfe"
    DEBUG = True