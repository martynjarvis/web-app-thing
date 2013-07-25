from wallet import app
from models import User,Api,Character,Transaction
from decorators import login_required

from google.appengine.ext import ndb

from flask import render_template, flash, url_for, redirect, request, session

from eveapi import EVEAPIConnection
from eveapi import Error as api_error

import datetime
import hashlib

# app methods
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        if request.form['username'] is None:
            flash('Invalid username','error')
            error = 'Invalid username'
        elif request.form['password1'] != request.form['password2'] :
            flash('Passwords do not match','error')
            error = 'Passwords do not match'   
        else :
            password_hash = (hashlib.md5(request.form['password1'].encode()).hexdigest())
            newUser = User(
                username = request.form['username'],
                email = request.form['email'],
                password = password_hash)
            newUser.put()
            session['logged_in'] = True
            session['username'] = request.form['username']
            session['userkey'] = newUser.key.urlsafe()
            flash('User created','success')
            return redirect(url_for('index'))
    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        loggingUser = User._get_by_username(request.form['username'])
        if loggingUser is None:
            flash('Invalid username','error')
            error = 'Invalid username'
        else :
            password_hash = (hashlib.md5(request.form['password'].encode()).hexdigest())
            if loggingUser.password != password_hash:
                flash('Invalid password','error')
                error = 'Invalid password'
            else :
                session['logged_in'] = True
                session['username'] = request.form['username']
                session['userkey'] = loggingUser.key.urlsafe()
                flash('You were logged in','success')
                return redirect(url_for('index'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('userkey', None)
    flash('You were logged out','warning')
    return redirect(url_for('index'))

@app.route('/')
def index():
    ''' Standard home page '''
    if 'username' in session.keys() :
        return redirect(url_for('api'))
    return render_template('index.html', title="Home")

@app.route('/api')
@login_required
def api():
    ''' List of APIs '''
    userKey = ndb.Key(urlsafe=session['userkey']) 
    apis = Api.query().filter(Api.user == userKey)
    return render_template('api.html', title="APIs", data=apis)
  
def update_char_from_api(keyID,vCode):
    userKey = ndb.Key(urlsafe=session['userkey'])  
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
        c.user = userKey
        c.characterID=int(character.characterID)
        c.characterName=character.name
        c.corporationID=int(character.corporationID)
        c.corporationName=character.corporationName
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

        userKey = ndb.Key(urlsafe=session['userkey']) 
        a = Api(user = userKey,
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
    userKey = ndb.Key(urlsafe=session['userkey']) 
    chars = Character.query().filter(Character.user == userKey)
    return render_template('characters.html', title="Characters", data=chars)


@app.route('/transactions')
@login_required
def transactions():
    ''' List transactions in db for this user'''
    # get chars
    userKey = ndb.Key(urlsafe=session['userkey']) 
    chars = Character.query().filter(Character.user == userKey).fetch(keys_only=True)
    # then get data
    data = Transaction.query(Transaction.character.IN(chars)).order(-Transaction.transactionID).fetch(200)
    return render_template('transactions.html', title="Transactions", data=data )
    
    