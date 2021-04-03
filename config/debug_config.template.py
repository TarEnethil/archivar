from config.user_config import UserConfig


class DebugConfig(UserConfig):
    """
    Debug Config Class
    inherits from UserConfig, because we want to run debug mode with the user's configuration + debug options
    """

    DEBUG = True
    # ENABLE_TOOLBAR = True
    # TOOLBAR_OPTIONS= [("INTERCEPT_REDIRECTS", True), ("TEMPLATE_EDITOR_ENABLED", True), ("PROFILER_ENABLED", True)]
    # LOG_SQL_QUERIES = True
    # TRACE_SQL_QUERIES = True
