from functools import wraps
from google.appengine.api import users
from flask import redirect, request, session, render_template

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
    
    
def trust_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not "Eve_Charid" in request.headers :
            return render_template('trust.html', title="Request Trust",redirect=func.__name__)
        return func(*args, **kwargs)
    return decorated_view
    
