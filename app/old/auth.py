from flask import session
import hashlib
from sqlalchemy.exc import IntegrityError

from evewallet.webapp import models, db

def current_user():
    user_id = session.get('user',None)
    user = db.session.query(models.User).get(user_id)
    return user

def logout():
    session.pop('user', None)
    return

def login(username,password):
    hash = hashlib.sha1(password).hexdigest()
    user = db.session.query(models.User).\
            filter(models.User.username==username).first()
    if user is not None and user.hash == hash:
        session['user'] = user.id
        return user
    return

def register(username, email, password):
    password_hash = hashlib.sha1(password).hexdigest()
    user = models.User(username=username,
                        email=email,
                        hash=password_hash)
    db.session.add(user)
    try:
        db.session.commit()  #TODO, deal with erro
    except IntegrityError:
        db.session.rollback()
        return None
    return user

