from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask.ext.login import login_required

from app import db
from .forms import ApiForm
from .models import Api, Character, Corporation
import tasks

api = Blueprint('api', __name__)

@api.route('/api')
@login_required
def apis():
    ''' List of APIs '''
    api_keys = db.session.query(Api).all()
    return render_template('api/api.html', title="APIs", data=api_keys)

@api.route('/api_add', methods=['GET', 'POST'])
@login_required
def add():
    ''' Adds an API to the db'''
    form = ApiForm()
    if form.validate_on_submit():
        api = Api()
        form.populate_obj(api)
        api.populate_from_object(form.key)
        if api.type in ('Account', 'Character'):
            for c in form.key.characters:
                character = Character.get_or_create(characterID=c.characterID)
                character.populate_from_object(c)
                api.characters.append(character)
                tasks.character_sheet.apply_async(countdown=1,
                                                  kwargs={'keyID': form.keyID.data,
                                                          'vCode': form.vCode.data,
                                                          'characterID': c.characterID})
        if api.type == 'Corporation':
            c = form.key.characters[0]
            corporation = Corporation.get_or_create(corporationID=c.corporationID)
            corporation.populate_from_object(c)
            api.corporations.append(corporation)
            tasks.corporation_sheet.apply_async(countdown=1,
                                                kwargs={'keyID': form.keyID.data,
                                                        'vCode': form.vCode.data})
        db.session.add(api)
        db.session.commit()
        return redirect(url_for('api.apis'))
    return render_template('api/add.html', form=form)

@api.route('/api_delete/<api_id>')
@login_required
def delete(api_id):
    ''' removes an API from the db'''
    this_api = db.session.query(Api).get(api_id)
    if api is None:
        flash('API Error','error')
        return redirect(url_for('api.apis'))
    db.session.delete(this_api)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash('API Error','error')
    return redirect(url_for('api.apis'))

@api.route('/api_refresh/<api_id>')
@login_required
def refresh(api_id):
    ''' refresh an API'''
    this_api = db.session.query(Api).get(api_id)
    tasks.corporation_sheet.apply_async(kwargs={'keyID': this_api.keyID,
                                                'vCode': this_api.vCode})
    #for c in this_api.characters:
        #tasks.character_sheet.apply_async(kwargs={'keyID': this_api.keyID,
                                                  #'vCode': this_api.vCode,
                                                  #'characterID': c.characterID})
    return redirect(url_for('api.apis'))

@api.route('/characters')
@login_required
def characters():
    ''' List characters in db linked to this user '''
    chars = db.session.query(Character).all()
    return render_template('api/characters.html', title="Characters", data=chars)

@api.route('/corporations')
@login_required
def corporations():
    ''' List corporations in db linked to this user '''
    corps = db.session.query(Corporation).all()
    return render_template('api/corporations.html', title="corporations", data=corps)

