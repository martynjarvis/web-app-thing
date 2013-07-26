from wallet import app
from models import Api,Character,Transaction,Order,Asset
from decorators import login_required

from google.appengine.ext import ndb
from google.appengine.api import users

from flask import render_template, flash, url_for, redirect, request, session

from eveapi import EVEAPIConnection
from eveapi import Error as api_error

import datetime
import hashlib

#TODO
# somehow add static database dump, I only need limited information
# market information, obviously can't add orders as I have on mysql

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You were logged out','warning')
    return redirect(users.create_logout_url(url_for('index')))
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if not users.get_current_user():
        return redirect(users.create_login_url(url_for('index')))
    else:
        return redirect(url_for('index'))
    
@app.route('/')
def index():
    ''' Standard home page '''
    if users.get_current_user():
        return redirect(url_for('api'))
    return render_template('index.html', title="Home")

@app.route('/api')
@login_required
def api():
    ''' List of APIs '''
    apis = Api.query().filter(Api.user == users.get_current_user())
    return render_template('api.html', title="APIs", data=apis)
  
def update_char_from_api(keyID,vCode):
    apiCon = EVEAPIConnection()
    auth = apiCon.auth(keyID=keyID, vCode=vCode)
    try: # Try calling api with given account
        account_status = auth.account.AccountStatus()
    except api_error, e:
        flash('API related error','error')
        return 
    except Exception, e:
        flash('unknown error','error')
        return 
    charList = []
    for character in auth.account.Characters().characters:
        q = Character.query().filter(Character.characterID == character.characterID).fetch(1)
        if q:
            c = q[0]
        else :
            c = Character()
        c.user = users.get_current_user()
        c.characterID=int(character.characterID)
        c.characterName=character.name
        #c.corporationID=int(character.corporationID)
        #c.corporationName=character.corporationName
        c.put()
        charList.append(c.key)
    return charList
    
@app.route('/api_add', methods=['GET', 'POST'])
@login_required
def api_add():
    ''' Adds an API to the db'''
    error = None
    if request.method == 'GET':
        return render_template('api_add.html',error=error)
    if request.method == 'POST':
        if request.form['api_id']=="" or request.form['api_vcode']=="":
            return render_template('api_add.html', error='Invalid API')
        
        charList = update_char_from_api(int(request.form['api_id']),vCode=request.form['api_vcode'])
        if not charList :
            render_template('api_add.html', error="Error:")

        a = Api(user = users.get_current_user(),
                keyID = int(request.form['api_id']),
                vCode=request.form['api_vcode'],
                characters = charList )
        a.put()
        return redirect(url_for('api'))

@app.route('/api_refresh/<apiKey>')
@login_required
def api_refresh(apiKey):
    ''' Refreshes an existing API to the db and adds new characters '''
    api = ndb.Key(urlsafe=apiKey).get()
    if api:
        a = update_char_from_api(api.keyID,api.vCode)
    else :
        flash('API related error','error')
    return redirect(url_for('api'))
        
        
@app.route('/characters')
@login_required
def characters():
    ''' List characters in db linked to this user '''
    chars = Character.query().filter(Character.user == users.get_current_user())
    return render_template('characters.html', title="Characters", data=chars)


@app.route('/transactions')
@login_required
def transactions():
    ''' List transactions in db for this user'''
    data = Transaction.query().order(-Transaction.transactionID).filter(Transaction.user == users.get_current_user()).fetch(100)
    return render_template('transactions.html', title="Transactions", data=data )
    
    
@app.route('/orders')
@login_required
def orders():
    ''' List transactions in db for this user'''
    data = Order.query(Order.user == users.get_current_user()).fetch()
    return render_template('orders.html', title="Orders", data=data )
    
@app.route('/assets')
@login_required
def assets():
    ''' List transactions in db for this user'''
    data = Asset.query(Asset.user == users.get_current_user()).fetch()
    return render_template('assets.html', title="Assets", data=data )
    

