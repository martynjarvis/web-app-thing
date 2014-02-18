from webapp import db

from functools import wraps
from flask import redirect, request, session, render_template, url_for
from models import Cache
import datetime

def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if 'user' not in session: # this is bad TODO
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return decorated_view
    
def trust_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not "Eve_Charid" in request.headers :
            return render_template('trust.html', title="Request Trust",redirect=func.__name__)
        return func(*args, **kwargs)
    return decorated_view
    
    
def cache(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        cache = Cache.get(kwargs['entity'].name,func.__name__)
        if cache is None:
            cache = Cache(kwargs['entity'].name,func.__name__)
            db.session.add(cache)
        if cache.cachedUntil is None or cache.cachedUntil < datetime.datetime.now():
            cachedUntil = func(*args, **kwargs)
            cache.cachedUntil = cachedUntil
            return
        else:
            return 
    return decorated_view