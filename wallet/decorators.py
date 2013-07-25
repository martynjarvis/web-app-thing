from functools import wraps
from google.appengine.api import users
from flask import redirect, request, session

def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not users.get_current_user():
            session['logged_in'] = False
            session['username'] = None
            return redirect(users.create_login_url(request.url))
        # TODO, don't do this every page view it is dumb
        session['logged_in'] = True
        session['username'] = users.get_current_user().nickname()
        return func(*args, **kwargs)
    return decorated_view