from flask import (Blueprint, redirect, render_template, request, session,
                   url_for)
from flask_login import login_required, login_user, logout_user

from app import eve, db
from .models import User
from .tools import auth_connection

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
    with auth_connection() as con:
        return render_template('sso/main.html', data=con.whoami(), con=con)


@sso.route('/sso/refresh')
@login_required
def sso_refresh():
    with auth_connection() as con:
        con.refresh()
    return redirect(url_for('sso.sso_main'))
