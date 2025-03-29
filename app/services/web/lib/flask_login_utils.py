from functools import wraps
from flask_login import current_user
from flask import redirect, url_for

def authorized_role(role):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if str(current_user.role).lower() != role.lower():
                return redirect(url_for('analysis.home'))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

