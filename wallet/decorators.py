from functools import wraps
#from google.appengine.api import users
from flask import redirect, request, url_for,session

def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        #if not users.get_current_user():
        if not 'username' in session.keys() :
            return redirect(url_for('login'))
            #return redirect(users.create_login_url(request.url))
        return func(*args, **kwargs)
    return decorated_view