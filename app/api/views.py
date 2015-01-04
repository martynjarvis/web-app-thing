from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask.ext.login import login_required

from app import db, app
from .forms import ApiForm
from .models import Api, Character, Corporation

api = Blueprint('api', __name__)

@app.route('/api')
@login_required
def apis():
    ''' List of APIs '''
    api_keys = db.session.query(Api).all()
    return render_template('api/api.html', title="APIs", data=api_keys)

@app.route('/api_add', methods=['GET', 'POST'])
@login_required
def api_add():
    ''' Adds an API to the db'''
    form = ApiForm()
    if form.validate_on_submit():
        api = Api()
        form.populate_obj(api)
        db.session.add(api)
        db.session.commit()
        return redirect(url_for('apis'))
    return render_template('api/add.html', form=form)

@app.route('/api_delete/<api_id>')
@login_required
def delete(api_id):
    ''' removes an API from the db'''
    api = db.session.query(Api).get(id)
    if api is None:
        flash('API Error','error')
        return redirect(url_for('apis'))
    db.session.delete(api)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash('API Error','error')
    return redirect(url_for('apis'))

@app.route('/characters')
@login_required
def characters():
    ''' List characters in db linked to this user '''
    chars = db.session.query(Character).all()
    return render_template('api/characters.html', title="Characters", data=chars)

@app.route('/corporations')
@login_required
def corporations():
    ''' List corporations in db linked to this user '''
    corps = db.session.query(Corporation).all()
    return render_template('api/corporations.html', title="corporations", data=corps)

