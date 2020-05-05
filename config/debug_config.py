from config.user_config import UserConfig

"""
Debug Config Class
inherits from UserConfig, because we want to run debug mode with the user's configuration + debug options
"""
class DebugConfig(UserConfig):
    SECRET_KEY = "debugging4lyfe"
    DEBUG = True
    #ENABLE_TOOLBAR = True
    #TOOLBAR_OPTIONS= [("INTERCEPT_REDIRECTS", False), ("TEMPLATE_EDITOR_ENABLED", True), ("PROFILER_ENABLED", False)]
    #LOG_SQL_QUERIES = True
    #TRACE_SQL_QUERIES = True