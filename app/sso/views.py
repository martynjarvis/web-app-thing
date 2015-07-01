import time

from flask import Blueprint, redirect, render_template, request, session, url_for
from flask.ext.login import login_required, login_user, logout_user, current_user

from app import eve, db
from .models import User

sso = Blueprint('sso', __name__)

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
        # first log in
        user = User()
        user.character_owner_hash = unicode(verify_data['CharacterOwnerHash'])
        user.character_id = verify_data['CharacterID']
        user.character_name = verify_data['CharacterName']
        user.expires = con.expires
        user.token = con.token
        user.refresh_token = con.refresh_token
        db.session.add(user)

    user.expires = con.expires
    user.token = con.token
    user.refresh_token = con.refresh_token
    db.session.commit()

    login_user(user)

    return render_template('crest/main.html', data=con.whoami())

@sso.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@sso.route('/sso')
@login_required
def sso_main():
    con = current_user.to_connection()
    return render_template('crest/main.html', data=con.whoami())
