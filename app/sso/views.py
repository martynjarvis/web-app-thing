import time

from flask import Blueprint, redirect, render_template, request, session, url_for
from flask.ext.login import login_required, login_user, logout_user, current_user

from pycrest.eve import AuthedConnection

from app import eve, db
from .models import User

sso = Blueprint('sso', __name__)

def get_connection():
    access_token, refresh_token, expires = session['eve_sso_data']
    res = {'access_token': access_token,
           'refresh_token': refresh_token,
           'expires_in': 0}
    con = AuthedConnection(
        res,
        endpoint=eve._authed_endpoint,
        oauth_endpoint=eve._oauth_endpoint,
        client_id=eve.client_id,
        api_key=eve.api_key,
        )
    if expires - int(time.time()) < 20:
        con.refresh()
        expires = con.expires
        refresh_token = con.refresh_token
        session['eve_sso_data'] = (access_token, refresh_token, expires)
    else:
        con.expires = expires

    return con

@sso.route('/login')
def sso_login():
    return redirect(eve.auth_uri(scopes=['publicData'], state="foobar"))

@sso.route('/callback')
def sso_callback():
    code = request.args.get('code')

    con = eve.authorize(code)

    verify_data = con.whoami()

    user = User.query.get(verify_data['CharacterOwnerHash'])

    if user is None:
        # First log in
        user = User()
        user.character_owner_hash = unicode(verify_data['CharacterOwnerHash'])
        user.character_id = verify_data['CharacterID']
        user.character_name = verify_data['CharacterName']
        db.session.add(user)
        db.session.commit()

    session['eve_sso_data'] = (con.token, con.refresh_token, con.expires)
    login_user(user)

    return redirect(url_for('sso.sso_main'))

@sso.route('/logout/')
@login_required
def logout():
    logout_user()
    session.pop('eve_sso_data', None)
    return redirect(url_for('index'))

@sso.route('/sso')
@login_required
def sso_main():
    con = get_connection()
    return render_template('sso/main.html', data=con.whoami(), con=con)

