from app.helpers import debug_mode
from flask import flash, redirect, url_for
from flask_login import current_user
from functools import wraps


# @admin_required decorater, use AFTER login_required
def admin_required(url="index"):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_admin():
                flash("You need to be admin to perform this action.", "danger")
                return redirect(url_for(url))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# @moderator decorater, use AFTER login_required
def moderator_required(url="index"):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_at_least_moderator():
                flash("You need to be moderator or admin to perform this action.", "danger")
                return redirect(url_for(url))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# @debug_mode_required decorator, use AFTER login_required
def debug_mode_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not debug_mode():
            # TODO: add link to README / documentation on how to activate it
            flash("This endpoint is only available in debug-mode.", "danger")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    return decorated_function
