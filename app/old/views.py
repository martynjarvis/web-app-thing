from flask import render_template, flash, url_for, redirect, request

from evewallet.webapp import app, decorators, auth, xmlapi, project

@app.route('/logout')
def logout():
    auth.logout()
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = auth.login(request.form['username'],request.form['password'])
        if user is not None:
            flash('You were logged in','success')
            return redirect(url_for('index'))
        flash('Incorrect username or password','error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.form['password1']==request.form['password2'] :
            user = auth.register(request.form['username'],request.form['email'],request.form['password1'])
            if user is not None:
                auth.login(request.form['username'],request.form['password1'])
                return redirect(url_for('index'))
            else:
                flash('Username already in use','error')
        else:
            flash('Passwords do not match','error')
    return render_template('register.html')

@app.route('/')
def index():
    ''' Standard home page '''
    return render_template('index.html', title="Home")

@app.route('/api')
@decorators.login_required
def apis():
    ''' List of APIs '''
    api_keys = xmlapi.all_keys()
    return render_template('api.html', title="APIs", data=api_keys)

@app.route('/api_add', methods=['GET', 'POST'])
@decorators.login_required
def api_add():
    ''' Adds an API to the db'''
    if request.method == 'POST':
        api = xmlapi.add_api(request.form['api_id'], request.form['api_vcode'])
        if api is not None:
            return redirect(url_for('apis'))
        else:
            flash('API Error','error')
    return render_template('api_add.html')

@app.route('/api_delete/<api_id>')
@decorators.login_required
def api_delete(api_id):
    ''' removes an API from the db'''
    if xmlapi.delete_api(api_id) is None:
        flash('API Error','error')
    return redirect(url_for('apis'))

@app.route('/characters')
@decorators.login_required
def characters():
    ''' List characters in db linked to this user '''
    chars = xmlapi.all_characters()
    return render_template('characters.html', title="Characters", data=chars)

@app.route('/corporations')
@decorators.login_required
def corporations():
    ''' List corporations in db linked to this user '''
    corps = xmlapi.all_corporations()
    return render_template('corporations.html', title="corporations", data=corps)

@app.route('/projects')
@decorators.login_required
def projects():
    ''' List of Projectss '''
    project_list = project.all_projects()
    return render_template('projects.html', title="Projects", data=project_list)

@app.route('/project_add', methods=['GET', 'POST'])
@decorators.login_required
def project_add():
    ''' Adds a Project to the db'''
    if request.method == 'POST':
        prj = project.add_project(request.form['output_id'],
                                  int(request.form['output_quantity']))
        if prj is not None:
            return redirect(url_for('projects'))
        else:
            flash('Project Error','error')
    return render_template('project_add.html')

@app.route('/project_delete/<project_id>')
@decorators.login_required
def project_delete(project_id):
    ''' removes a Project from the db'''
    if project.delete_project(project_id) is None:
        flash('Project Error','error')
    return redirect(url_for('projects'))

@app.route('/project_view/<project_id>')
@decorators.login_required
def project_view(project_id):
    ''' List of Projectss '''
    prj = project.get_project(project_id)
    return render_template('project_view.html', title="Projects", data=prj)

# @app.route('/api_refresh/<apiKey>')
# @decorators.login_required
# def api_refresh(apiKey):
    # ''' Refreshes an existing API to the db and adds new characters '''

# # @app.route('/overview')
# # @login_required
# # def overview():
    # # ''' List characters in db linked to this user '''
    # # chars = Character.query().filter(Character.user == users.get_current_user())
    # # corps = Corporation.query().filter(Corporation.user == users.get_current_user())
    # # return render_template('overview.html', title="Overview", data={'chars':chars,'corps':corps})

# @app.route('/transactions')
# @decorators.login_required
# def transactions():
    # data = db.session.query(models.Transaction).all() #TODO this returns all transactions currently, need to think about this
    # return render_template('transactions.html', title="Transactions", data=data )

# @app.route('/orders')
# @decorators.login_required
# def orders():
    # data = db.session.query(models.Order).all()
    # return render_template('orders.html', title="Orders", data=data )

# @app.route('/assets')
# @decorators.login_required
# def assets():
    # data = db.session.query(models.Asset).all()
    # return render_template('assets.html', title="Assets", data=data )

# @app.route('/item/<typeID>')
# @decorators.login_required
# def item(typeID):
    # ''' List orders,transactions and assets'''
    # item = models.InvTypes.getByID(int(typeID))
    # return render_template('item.html', title=item.typeName, item=item)

# @app.route('/update')
# @app.route('/update/<importCost>')
# @decorators.trust_required
# def order_update(importCost=0):
    # '''Scans through items character currently has on market'''
    # charID = int(request.headers["Eve_Charid"])
    # regionID = int(request.headers["Eve_Regionid"])

    # query = db.session.query(models.Order, models.InvTypes, models.ItemPrice, models.StaStations)\
        # .filter(models.Order.orderState == 0)\
        # .filter(models.Order.charID == charID)\
        # .filter(models.Order.bid == False)\
        # .filter(models.Order.stationID == models.StaStations.stationID)\
        # .filter(models.StaStations.regionID == regionID)\
        # .filter(models.Order.typeID == models.InvTypes.typeID)\
        # .filter(models.InvTypes.typeID == models.ItemPrice.typeID)\
        # .filter(models.ItemPrice.transactionType == models.SELL)\
        # .filter(models.ItemPrice.solarsystemID == models.JITA)

    # markups = [1.0,1.05,1.1,1.15,1.2,1.25,1.30]

    # return render_template('update.html', title="Update Orders", data=query, import_cost=importCost,  markups=markups )

# @app.route('/import', methods=['GET', 'POST'])
# def import_tool():
    # '''Returns a list of items to import to a given system based on market history'''
    # # source="Jita"
    # # dest="K-6K16"
    # cost=275.
    # # if request.method == 'POST':
        # # source = request.form['source']
        # # dest = request.form['dest']
        # # cost = float(request.form['cost'])

    # sourcePrice = aliased(models.ItemPrice)
    # destPrice = aliased(models.ItemPrice)
    # # .join(sourcePrice.typeID, models.InvTypes.typeID)\
    # # .join(destPrice.typeID, models.InvTypes.typeID)\

    # data = db.session.query(models.InvTypes, sourcePrice.price, destPrice.price)\
        # .filter(models.InvTypes.marketGroupID is not None)\
        # .filter(models.InvTypes.marketGroupID < 300000)\
        # .filter(sourcePrice.typeID == models.InvTypes.typeID)\
        # .filter(sourcePrice.transactionType == models.SELL)\
        # .filter(sourcePrice.solarsystemID == models.JITA)\
        # .filter(destPrice.typeID == models.InvTypes.typeID)\
        # .filter(destPrice.transactionType == models.SELL)\
        # .filter(destPrice.solarsystemID == 30003862)\
        # .limit(10)

    # return render_template('import.html', title="Import", data=data, cost=cost)

# # @trust_required
# # @app.route('/list', methods=['GET', 'POST'])
# # def list_tool():
    # # '''tool for quickly listing items'''
    # # if request.method == 'POST':
        # # importCost = float(request.form['cost'])
        # # stuff = request.form['stuff']
        # # data = []
        # # typeIDs = [] # to keep track of repeats
        # # for line in stuff.split('\n'):
            # # typeName = line.split('\t')[0]
            # # item = Item.query().filter(Item.typeName == typeName).get()
            # # if item and not item.typeID in typeIDs :
                # # typeIDs.append(item.typeID)
                # # data.append([item.typeID,item.typeName,item.sell,item.sell+importCost*item.volume])
        # # data.sort(key=lambda x: x[1]) # sort by name
        # # return render_template('update.html', title="Update Orders", data=data, import_cost=importCost,  bid=0 )
    # # else :
        # # return render_template('list_tool.html', title="List Tool")#, data=data, import_cost=import_cost )

# # @app.route('/search', methods=['POST'])
# # def search():
    # # '''Returns a list of items matching search term'''
    # # if int(request.form['search_id']) > 0 : # autocomplete from typeahead
        # # return redirect(url_for('item',typeID=int(request.form['search_id'])))
    # # q = str(request.form['search_term'])
    # # data = Item.query().filter(Item.typeName>=q).filter(Item.typeName<q+ u"\ufffd").fetch(10)
    # # return render_template('search.html', title=request.form['search_term'], searchData=data, searchTerm=q)

