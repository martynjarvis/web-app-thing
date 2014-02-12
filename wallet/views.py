from wallet import app,db

import models
import decorators

from flask import render_template, flash, url_for, redirect, request, session

# from eveapi import EVEAPIConnection
# from eveapi import Error as api_error

import datetime
import hashlib
import logging

# TODO charactor page (similar to item page)

# TODO add corp apis
# market orders, same

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = models.User.auth(request.form['username'],request.form['password'])
        if user is not None:
            session['user'] = user.id
            flash('You were logged in','success')
            return redirect(url_for('index'))  
        flash('Incorrect username or password','error')
    return render_template('login.html')
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.form['password1']==request.form['password2'] :
            user = models.User(request.form['username'],request.form['email'],request.form['password1'])
            db.session.add(user)
            db.session.commit()  #TODO, deal with erro
            return redirect(url_for('index'))
        flash('Incorrect username or password','error')
    return render_template('register.html')

@app.route('/')
def index():
    ''' Standard home page '''
    #if 'user' in session:
    #    return redirect(url_for('overview'))
    return render_template('index.html', title="Home")

@app.route('/api')
@decorators.login_required
def api():
    ''' List of APIs '''
    user = models.User.get(session['user'])
    return render_template('api.html', title="APIs", data=user.apis)
    
@app.route('/api_add', methods=['GET', 'POST'])
@decorators.login_required
def api_add():
    ''' Adds an API to the db'''
    if request.method == 'GET':
        return render_template('api_add.html')
    if request.method == 'POST':
        if request.form['api_id']=="" or request.form['api_vcode']=="":
            flash('Invalid API','error')
            return render_template('api_add.html')
        api = models.Api(request.form['api_id'],request.form['api_vcode'],session['user'])
        if api.update() > 0 :
            flash('API Error','error')
            return render_template('api_add.html')
        else : 
            db.session.add(api)
        db.session.commit()
        return redirect(url_for('api'))
        
@app.route('/characters')
@decorators.login_required
def characters():
    ''' List characters in db linked to this user '''
    chars = db.session.query(models.Character).join(models.Api.characters).filter(models.Api.userId==session['user']).all()
    return render_template('characters.html', title="Characters", data=chars)    
    
@app.route('/corporations')
@decorators.login_required
def corporations():
    ''' List corporations in db linked to this user '''
    corps = db.session.query(models.Corporation).join(models.Api.corporation).filter(models.Api.userId==session['user']).all()
    return render_template('corporations.html', title="corporations", data=corps)  

# @app.route('/api_refresh/<apiKey>')
# @login_required
# def api_refresh(apiKey):
    # ''' Refreshes an existing API to the db and adds new characters '''
    # api = ndb.Key(urlsafe=apiKey).get()
    # if api:
        # auth = EVEAPIConnection().auth(keyID=api.keyID, vCode=api.vCode)
        # a = update_char_from_api(auth)
    # else :
        # flash('API related error','error')
    # return redirect(url_for('api'))
        
# @app.route('/overview')
# @login_required
# def overview():
    # ''' List characters in db linked to this user '''
    # chars = Character.query().filter(Character.user == users.get_current_user())
    # corps = Corporation.query().filter(Corporation.user == users.get_current_user())
    # return render_template('overview.html', title="Overview", data={'chars':chars,'corps':corps})
        
    
# @app.route('/corporations')
# @login_required
# def corporations():
    # ''' List characters in db linked to this user '''
    # corps = Corporation.query().filter(Corporation.user == users.get_current_user())
    # return render_template('corporations.html', title="Corporations", data=corps)

@app.route('/transactions')
@decorators.login_required
def transactions():
    data = db.session.query(models.Transaction).all() #TODO this returns all transactions currently, need to think about this    
    return render_template('transactions.html', title="Transactions", data=data )
    
@app.route('/orders')
@decorators.login_required
def orders():
    data = db.session.query(models.Order).all()
    return render_template('orders.html', title="Orders", data=data )
    
# @app.route('/assets')
# @login_required
# def assets():
    # ''' List transactions in db for this user'''
    # data = Asset.query().filter(Asset.user == users.get_current_user()).fetch()
    # return render_template('assets.html', title="Assets", data=data )
    
# @app.route('/item/<typeID>')
# @login_required
# def item(typeID):
    # ''' List orders,transactions and assets'''
    # typeID = int(typeID)
    # item         = Item.query().filter(Item.typeID == typeID).get()
    # if item is None:
        # return redirect(url_for('index')) # TODO change this tosomewhere useful
    # orders       = Order.query().filter(Order.user == users.get_current_user()).filter(Order.typeID == typeID).fetch()
    # transactions = Transaction.query().filter(Transaction.user == users.get_current_user()).filter(Transaction.typeID == typeID).fetch()
    # assets       = Asset.query().filter(Asset.user == users.get_current_user()).filter(Asset.typeID == typeID).fetch()
    # return render_template('item.html', title=item.typeName, item=item,orders=orders,transactions=transactions,assets=assets)

# @app.route('/update')
# @app.route('/update/<importCost>')
# @trust_required
# def order_update(importCost=0):
    # '''Scans through items character currently has on market'''
    # charID = int(request.headers["Eve_Charid"])
    # orders = Order.query().filter(Order.charID == charID).fetch()
    # data = []
    # typeIDs = [] # to keep track of repeats
    # for order in orders: # not ideal
        # item = Item.query().filter(Item.typeID == order.typeID).get()
        # if not item.typeID in typeIDs :
            # typeIDs.append(item.typeID)
            # data.append([order.typeID,order.typeName,item.sell,item.sell+importCost*item.volume])
    # return render_template('update.html', title="Update Orders", data=data, import_cost=importCost,  bid=0 )

# @trust_required
# @app.route('/list', methods=['GET', 'POST'])
# def list_tool():
    # '''tool for quickly listing items'''
    # if request.method == 'POST':
        # importCost = float(request.form['cost'])
        # stuff = request.form['stuff']
        # data = []
        # typeIDs = [] # to keep track of repeats
        # for line in stuff.split('\n'):
            # typeName = line.split('\t')[0]
            # item = Item.query().filter(Item.typeName == typeName).get()
            # if item and not item.typeID in typeIDs :
                # typeIDs.append(item.typeID)
                # data.append([item.typeID,item.typeName,item.sell,item.sell+importCost*item.volume])
        # data.sort(key=lambda x: x[1]) # sort by name  
        # return render_template('update.html', title="Update Orders", data=data, import_cost=importCost,  bid=0 )
    # else :
        # return render_template('list_tool.html', title="List Tool")#, data=data, import_cost=import_cost )
        
# @app.route('/search', methods=['POST'])
# def search():
    # '''Returns a list of items matching search term'''
    # if int(request.form['search_id']) > 0 : # autocomplete from typeahead
        # return redirect(url_for('item',typeID=int(request.form['search_id'])))
    # q = str(request.form['search_term'])
    # data = Item.query().filter(Item.typeName>=q).filter(Item.typeName<q+ u"\ufffd").fetch(10)
    # return render_template('search.html', title=request.form['search_term'], searchData=data, searchTerm=q)   
    

        
        