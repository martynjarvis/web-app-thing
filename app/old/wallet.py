# -*- coding: utf-8 -*-
'''
    Wallet
    ~~~~~~
    Web app for checking my transactions.
    Built on top of flaskr tutorial.
'''

# TODO LIST
# Sort out buy orders and escrow related bugs
# Add corporation api options
# Industry job tracking


from flask import Flask,jsonify, request, session, g, redirect, url_for, abort, \
     render_template, flash, _app_ctx_stack
import pymysql
import hashlib
from lib.eveapi import EVEAPIConnection
from lib.eveapi import Error as api_error
from datetime import timedelta, datetime
import json

# configuration
DATABASE = './flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'

# setup app
app = Flask(__name__)
app.config.from_object(__name__)

# database methods
def get_db():
    top = _app_ctx_stack.top
    if not hasattr(top, 'mysql_db'):
        top.mysql_db = pymysql.connect(host="localhost",port=3306,user="test",passwd="pleaseignore",db="wallet")
    return top.mysql_db

@app.teardown_appcontext
def close_db_connection(exception):
    '''Closes the database again at the end of the request.'''
    top = _app_ctx_stack.top
    if hasattr(top, 'mysql_db'):
        top.mysql_db.close()

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
            db = get_db()
            cur = db.cursor()
            try :
                cur.execute("INSERT INTO user (username,email,password_hash) VALUES(%s,%s,%s)",
                    (request.form['username'], request.form['email'],password_hash))
                db.commit()
            except Exception, e:
                flash(e,'error')
                return render_template('register.html', error= e)

            cur.execute("SELECT id FROM user WHERE username=%s", [request.form['username']])
            result = cur.fetchone()
            session['logged_in'] = True
            session['username'] = request.form['username']
            session['userid'] = result[0]
            flash('User created','success')
            return redirect(url_for('index'))
            
    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT id,password_hash FROM user WHERE username=%s", [request.form['username']])
        result = cur.fetchone()
        if result is None:
            flash('Invalid username','error')
            error = 'Invalid username'
        else :
            userid,saved_hash = result
            password_hash = (hashlib.md5(request.form['password'].encode()).hexdigest())
            if saved_hash != password_hash:
                flash('Invalid password','error')
                error = 'Invalid password'
            else :
                session['logged_in'] = True
                session['username'] = request.form['username']
                session['userid'] = userid
                flash('You were logged in','success')
                return redirect(url_for('index'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('userid', None)
    flash('You were logged out','warning')
    return redirect(url_for('index'))

@app.route('/')
def index():
    ''' Standard home page '''
    if 'userid' in session.keys() :
        return redirect(url_for('overview'))
    return render_template('index.html', title="Home")

@app.route('/api')
def api():
    ''' List of APIs '''
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id,vcode FROM api WHERE user_id=%s",session['userid']);
    data = cur.fetchall()
    return render_template('api.html', title="APIs", data=data)

@app.route('/api_add', methods=['GET', 'POST'])
def api_add():
    ''' Adds an API to the db'''
    error = None
    if request.method == 'GET':
        return render_template('api_add.html',error=error)
    if request.method == 'POST':
        if request.form['api_id']=="" or request.form['api_vcode']=="":
            return render_template('api_add.html', error='Invalid API')
        db = get_db()
        cur = db.cursor()
        api_con = EVEAPIConnection()
        auth = api_con.auth(keyID=request.form['api_id'], vCode=request.form['api_vcode'])
        try: # Try calling api with given account
            account_status = auth.account.AccountStatus()
        except api_error, e:
            flash('API related error','error')
            return render_template('api_add.html', error="API error:" + str(e))
        except Exception, e:
            return render_template('api_add.html', error="Unknown error:" + str(e))
        cur.execute("INSERT INTO api (id,vcode,user_id) VALUES(%s,%s,%s)",
                 [request.form['api_id'], request.form['api_vcode'], session['userid']])
        char_list = auth.account.Characters()
        for character in char_list.characters:
            cur.execute('''INSERT INTO chara (id,name,api_id) VALUES(%s,%s,%s)
                on duplicate key update api_id=%s''', [int(character.characterID), character.name, request.form['api_id'], request.form['api_id']])
        try:
            db.commit()
        except:
            return render_template('api_add.html', error="Database error:" + str(sys.exc_info()[0]) )
        return redirect(url_for('api'))

@app.route('/api_refresh/<api_id>')
def api_refresh(api_id):
    ''' Refreshes an existing API to the db and adds new characters '''
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT api.id,api.vcode FROM api WHERE api.id=%s",api_id);
    data = cur.fetchone()
    if data :
        api_con = EVEAPIConnection()
        auth = api_con.auth(keyID=data[0], vCode=data[1])
        try: # Try calling api with given account
            account_status = auth.account.AccountStatus()
        except api_error, e:
            flash('API related error','error')
            return redirect(url_for('api'))
        except Exception, e:
            flash('Unknown related error','error')
            return redirect(url_for('api'))
        char_list = auth.account.Characters()
        for character in char_list.characters:
            cur.execute('''INSERT INTO chara (id,name,api_id) VALUES(%s,%s,%s)
                on duplicate key update api_id=%s''', [int(character.characterID), character.name, api_id, api_id])
        try:
            db.commit()
        except:
            flash('Database related error','error')
            return redirect(url_for('api'))
        flash('Updated character list.','success')
        return redirect(url_for('api'))

@app.route('/api_delete/<api_id>')
def api_delete(api_id):
    ''' Deletes an existing API and nulls the characters api value
    UNSAFE!! No check on who owns the API!!!!!
    '''
    db = get_db()
    cur = db.cursor()
    cur.execute("UPDATE chara SET api_id=NULL WHERE api_id=%s", api_id)
    cur.execute("DELETE FROM api WHERE id=%s", api_id)
    db.commit()
    try:
        db.commit()
    except:
        flash('Database related error','error')
        return redirect(url_for('api'))
    flash('Removed API.','success')
    return redirect(url_for('api'))

@app.route('/characters')
def characters():
    ''' List characters in db linked to this user '''
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT chara.id,chara.name FROM chara,api WHERE chara.api_id=api.id AND api.user_id=%s",session['userid']);
    data = cur.fetchall()
    return render_template('characters.html', title="Characters", data=data )

@app.route('/transactions')
def transactions():
    ''' List transactions in db for this user'''
    db = get_db()
    cur = db.cursor()
    cur.execute('''SELECT chara.id, chara.name, wallet_trans.transaction_time,\
        wallet_trans.quantity, wallet_trans.type_name, wallet_trans.type_id,\
        wallet_trans.price, wallet_trans.station_id, wallet_trans.station_name,\
        wallet_trans.transaction_type FROM wallet_trans,chara,api WHERE\
        wallet_trans.char_id = chara.id AND chara.api_id=api.id AND\
        api.user_id=%s\
        ORDER BY wallet_trans.transaction_time DESC''',session['userid']);
    data = cur.fetchmany(2000)
    return render_template('transactions.html', title="Transactions", data=data )

@app.route('/orders')
def orders():
    ''' List orders in db for this user'''
    db = get_db()
    cur = db.cursor()
    cur.execute('''SELECT chara.id, chara.name,
        wallet_order.id, wallet_order.vol_entered, wallet_order.vol_remaining,
        wallet_order.type_id, eve.invtypes.typeName,
        wallet_order.price,wallet_order.bid, wallet_order.issued,
        wallet_order.station_id, station_un.name
        FROM wallet_order,chara,api,user,eve.invtypes,
        (select * from ( select stationID id, stationName name from outpost UNION select stationID id, stationName name from eve.stastations ) as test group by id ) as station_un
        WHERE wallet_order.type_id=eve.invtypes.typeID
        AND wallet_order.station_id = station_un.id
        AND wallet_order.order_state=0
        AND wallet_order.char_id = chara.id
        AND chara.api_id=api.id
        AND api.user_id=%s''',session['userid'])
    data = cur.fetchall()

    sell_orders = {}
    buy_orders = {}
    for row in data:
        cha = row[0] # char id
        sta = row[10] # station id
        ord = row[2] # asset id
        pri = float(row[7])

        if row[8]==0: # sell order
            if cha not in sell_orders.keys():
                sell_orders[cha] = {"name":row[1],
                                "stations":{},
                                "total":0.0}

            if sta not in sell_orders[cha]["stations"].keys(): # add locations here
                sell_orders[cha]["stations"][sta] = {"name":row[11],
                                                "orders":{},
                                                "total":0.0}
            sell_orders[cha]["stations"][sta]["orders"][ord] = {
                "vol_entered":row[3],
                "vol_remaining":row[4],
                "id":row[5],
                "name":row[6],
                "price":row[7],
                "issued":row[9]}

            sell_orders[cha]["stations"][sta]["total"]+=pri*row[4]
            sell_orders[cha]["total"]+=pri*row[4]

        else : # buy order
            if cha not in buy_orders.keys():
                buy_orders[cha] = {"name":row[1],
                                "stations":{},
                                "total":0.0}

            if sta not in buy_orders[cha]["stations"].keys(): # add locations here
                buy_orders[cha]["stations"][sta] = {"name":row[11],
                                                "orders":{},
                                                "total":0.0}
            buy_orders[cha]["stations"][sta]["orders"][ord] = {
                "vol_entered":row[3],
                "vol_remaining":row[4],
                "id":row[5],
                "name":row[6],
                "price":row[7],
                "issued":row[9]}

            buy_orders[cha]["stations"][sta]["total"]+=pri*row[4]
            buy_orders[cha]["total"]+=pri*row[4]   # TODO this is misleading due to "margin trading" skill

    return render_template('orders.html', title="Orders", sell_orders=sell_orders, buy_orders=buy_orders)




@app.route('/item/<item_id>')
def item(item_id):
    ''' Detailed information on market stats, transactions and
    orders in db for this user'''
    db = get_db()
    cur = db.cursor()

    #item stats
    cur.execute("SELECT typeName,volume,marketGroupID FROM eve.invtypes WHERE typeID=%s",[item_id])
    item_data = cur.fetchone()
    market_group = item_data[2]
    item_data = {"id":item_id, "name":item_data[0], "volume":item_data[1]}

    # create bread crumbs
    tree = []
    parent = market_group
    while parent :
      cur.execute("SELECT parentGroupID,marketGroupID,marketGroupName FROM eve.invmarketgroups WHERE marketGroupID=%s",[parent])
      market = cur.fetchone()
      parent = market[0]
      tree.append([market[2],market[1]])

    # orders
    cur.execute('''SELECT chara.id, chara.name, wallet_order.station_id,\
        wallet_order.vol_entered, wallet_order.vol_remaining,\
        wallet_order.min_vol, wallet_order.order_state,\
        wallet_order.order_range,\
        wallet_order.duration, wallet_order.escrow, wallet_order.price,\
        wallet_order.bid, wallet_order.issued \
        FROM wallet_order,chara,api,user \
        WHERE wallet_order.type_id=%s \
        AND wallet_order.order_state=0
        AND wallet_order.char_id = chara.id \
        AND chara.api_id=api.id \
        AND api.user_id=%s''',[item_id,session['userid']])
    order_data = cur.fetchall()

    # market history
    cur.execute('''SELECT date,avg_price
                   FROM market_hist
                   WHERE type_id=%s
                   AND region_id=10000002
                   ORDER BY date ''',[item_id])
    hist_data = cur.fetchall()

    # market data
    cur.execute('''
        SELECT min(price)
        FROM market_order
        WHERE type_id=%s
        AND solarsystem_id=30000142
        AND bid=0
        ''',[item_id])
    market_data = cur.fetchone()

    # transaction data
    cur.execute('''SELECT chara.id, chara.name, wallet_trans.transaction_time,\
        wallet_trans.quantity, \
        wallet_trans.price, wallet_trans.station_id, wallet_trans.station_name,\
        wallet_trans.transaction_type \
        FROM wallet_trans,chara,api,user \
        WHERE wallet_trans.type_id = %s \
        AND wallet_trans.char_id = chara.id \
        AND chara.api_id=api.id \
        AND api.user_id=%s\
        ORDER BY wallet_trans.transaction_time DESC''', [item_id,session['userid']]);
    transaction_data = cur.fetchall()

    sold_vol = sold_profit = buy_vol = buy_profit = sold_30 = sold_7 = 0
    last_buy = last_sell = profit_total = None
    for transaction in transaction_data:
        if transaction[7] == "sell" :
            sold_vol += transaction[3]#quantity
            sold_profit += float(transaction[3]*transaction[4])#quant x price
            age = abs(datetime.utcnow()-transaction[2])
            if age.days<30:
                sold_30 += transaction[3]
            if age.days<7:
                sold_7 += transaction[3]
            if not last_sell: last_sell = float(transaction[4])
        elif transaction[7] == "buy" :
            buy_vol += transaction[3]
            buy_profit += float(transaction[3]*transaction[4])
            if not last_buy: last_buy = float(transaction[4])
    if buy_vol > 0 : profit_total = sold_profit-buy_profit*(float(sold_vol)/float(buy_vol))


    # data for the stats box
    stats_data = {"last_buy": last_buy,
                  "last_sell": last_sell,
                  "sold_total": sold_vol,
                  "profit_total": profit_total,
                  "sold_30": sold_30,
                  "sold_7": sold_7}

    return render_template('item.html', title=item_data["name"],
        transaction_data=transaction_data, order_data=order_data,
        item_data=item_data, stats_data=stats_data, market_data=market_data,
        hist_data=hist_data, tree=tree)

@app.route('/_typeahead_data')
def typeahead_data():
    db = get_db()
    cur = db.cursor()
    q = request.args.get('q', 0, type=str)
    sql = '''SELECT typeID, typeName
           FROM eve.invtypes
           WHERE typeName LIKE %s
           AND typeName NOT LIKE %s
           AND marketGroupID IS NOT NULL
           ORDER BY typeID '''

    cur.execute(sql , ("%"+q+"%", "%Blueprint"))
    search_data = cur.fetchmany(8)

    return jsonify(result=search_data)

@app.route('/search', methods=['POST'])
def search():
    '''Returns a list of items matching search term,
    called from search form in navbar'''
    if request.method == 'POST':
        if request.form['search_term']=="":
            flash('No search term entered','error')
            return redirect(url_for('market'))
    if int(request.form['search_id']) > 0 :
        return redirect(url_for('item',item_id=int(request.form['search_id'])))
    db = get_db()
    cur = db.cursor()
    sql = '''SELECT typeID, typeName
           FROM eve.invtypes
           WHERE typeName LIKE %s
           AND marketGroupID IS NOT NULL
           ORDER BY typeName '''
    cur.execute(sql , "%"+str(request.form['search_term'])+"%" )
    search_data = cur.fetchall()

    return render_template('search.html', title=request.form['search_term'],
        search_data=search_data, search_term=request.form['search_term'])

@app.route('/market')
@app.route('/market/<market_id>')
def market(market_id=None):
    '''Browse market groups and items'''
    db = get_db()
    cur = db.cursor()

    if market_id:
        cur.execute('''SELECT marketGroupName,marketGroupID
                       FROM eve.invmarketgroups
                       WHERE parentGroupID=%s''',[market_id])
    else :
        cur.execute('''SELECT marketGroupName,marketGroupID
                       FROM eve.invmarketgroups
                       WHERE parentGroupID IS NULL''')
    child_markets = cur.fetchall()
    child_items = []
    tree = []
    if market_id:
        cur.execute('''SELECT typeName,typeID
                   FROM eve.invtypes
                   WHERE marketGroupID=%s''',[market_id])
        child_items = cur.fetchall()

        # create bread crumbs, Markets groups are arranged in a tree structure we
        # recursivly query table until we get Null returned
        parent = market_id
        while parent :
            cur.execute('''SELECT parentGroupID,marketGroupID,marketGroupName
                            FROM eve.invmarketgroups
                            WHERE marketGroupID=%s''',[parent])
            market = cur.fetchone()
            parent = market[0]
            tree.append([market[2],market[1]])

    title = tree[0][0] if tree else "Market Browser"

    return render_template('market.html', title=title,
        child_markets=child_markets, child_items=child_items, tree=tree)

@app.route('/overview')
def overview():
    '''Detailed information on current and historical balances'''
    db = get_db()
    cur = db.cursor()

    cur.execute('''SELECT chara.name, balance.balance
        FROM balance,chara,api\
        WHERE balance.char_id = chara.id \
        AND chara.api_id=api.id \
        AND api.user_id=%s''', session['userid'])
    wallet_data = cur.fetchall()

    cur.execute('''SELECT chara.name, \
        SUM(wallet_order.price*wallet_order.vol_remaining) \
        FROM wallet_order,chara,api\
        WHERE wallet_order.bid=0 \
        AND wallet_order.order_state=0 \
        AND wallet_order.char_id=chara.id \
        AND chara.api_id=api.id \
        AND api.user_id=%s GROUP BY wallet_order.char_id''', session['userid'])
    sell_data = cur.fetchall()

    cur.execute('''SELECT chara.name, \
        SUM(wallet_order.escrow) \
        FROM wallet_order,chara,api,user\
        WHERE wallet_order.bid=1 \
        AND wallet_order.order_state=0 \
        AND wallet_order.char_id=chara.id \
        AND chara.api_id=api.id \
        AND api.user_id=%s GROUP BY wallet_order.char_id''',session['userid'])
    buy_data = cur.fetchall()
    # TODO This does not correctly take in to account how margin trading works

    cur.execute('''SELECT
        chara.name,
        SUM(COALESCE(asset.quantity*stat.sell,0))
        FROM
        asset LEFT OUTER JOIN
        (SELECT type_id,min(price) AS sell
        FROM market_order
        WHERE bid=0
        AND solarsystem_id=30000142
        GROUP BY type_id) stat ON asset.type_id=stat.type_id,
        chara,api,user
        WHERE (asset.raw_quantity <> -2 OR asset.raw_quantity IS Null)
        AND asset.chara_id = chara.id \
        AND chara.api_id=api.id \
        AND api.user_id=%s
        GROUP BY chara.id''',session['userid'])
    asset_data = cur.fetchall()

    net_worth = 0 
    for x,balance in wallet_data :
        net_worth+=balance
    for x,balance in sell_data :
        net_worth+=balance
    for x,balance in buy_data : 
        net_worth+=balance
        # TODO This does not correctly take in to account how margin trading works
    for x,balance in asset_data :
        net_worth+=balance

    cur.execute('''SELECT  wallet_hist.query_time,
                   wallet_hist.sell_orders, wallet_hist.buy_orders,
                   wallet_hist.liquid, wallet_hist.assets
                   FROM wallet_hist,user
                   WHERE wallet_hist.user_id=%s''',session['userid'])
    history_data = cur.fetchall()

    return render_template('overview.html',
                           title="Overview",
                           wallet_data=wallet_data,
                           sell_data=sell_data,
                           buy_data=buy_data,
                           asset_data=asset_data,
                           history_data=history_data,
                           net=net_worth)

@app.route('/import', methods=['GET', 'POST'])
def market_import():
    '''Returns a list of items to import to a given system based on market history'''
    source="Jita"
    dest="K-6K16"
    cost=275.
    if request.method == 'POST':
        source = request.form['source']
        dest = request.form['dest']
        cost = float(request.form['cost'])

    db = get_db()
    cur = db.cursor()

    # source system
    cur.execute("SELECT solarSystemID,regionID FROM eve.mapsolarsystems WHERE solarSystemName = %s" , [source] )
    source_data = cur.fetchone()
    source_data = { "name":source, "system_id":source_data[0], "region_id":source_data[1]}

    # dest system system
    cur.execute("SELECT solarSystemID,regionID FROM eve.mapsolarsystems WHERE solarSystemName = %s" , [dest] )
    dest_data = cur.fetchone()
    dest_data = {"name":dest, "system_id":dest_data[0], "region_id":dest_data[1]}
    cur.execute('''
      SELECT
      eve.invtypes.typeID, eve.invtypes.typeName,
      dest_hist.vol,
      source.sell,
      (source.sell+%s*eve.invtypes.volume),
      dest.prices,
      dest.vols,
      dest.competitors,
      TIMEDIFF(UTC_TIMESTAMP(),dest.age)
      FROM eve.invtypes,
      ( SELECT type_id, avg(avg_price) AS price , sum(volume)/4.0 AS vol
        FROM market_hist
        WHERE region_id=%s
        AND date > CURDATE() - INTERVAL 30 DAY
        GROUP BY type_id ) dest_hist,
      (SELECT type_id,min(price) AS sell
        FROM market_order
        WHERE bid=0
        AND solarsystem_id=%s
        GROUP BY type_id) source LEFT OUTER JOIN
      (SELECT type_id,min(price) AS sell,max(created) AS age,
        min(price) as prices,
        sum(vol_remaining) as vols,
        count(price) as competitors
        FROM market_order
        WHERE bid=0
        AND solarsystem_id=%s
        GROUP BY type_id) dest ON source.type_id=dest.type_id
      WHERE eve.invtypes.typeID = source.type_id
      AND dest_hist.type_id = source.type_id
      AND eve.invtypes.typeID != 17366
      AND (dest.sell/(source.sell+%s*eve.invtypes.volume)>1.25
      OR dest.sell IS NULL)
      AND dest_hist.price > 0.75*(source.sell+%s*eve.invtypes.volume)
      ORDER BY (source.sell+%s*eve.invtypes.volume)*0.2*dest_hist.vol DESC ''',(cost,dest_data["region_id"],source_data["system_id"],dest_data["system_id"],cost,cost,cost))
    data = cur.fetchmany(200)

    return render_template('import.html', title="Import", data=data,
        source_data=source_data, dest_data=dest_data, action="import", cost=cost)


@app.route('/stock', methods=['GET', 'POST'])
def market_stock():
    '''Returns a list of items to import to a given system based on ship losses'''
    source="Jita"
    dest="Karan"
    cost=300.
    if request.method == 'POST':
        source = request.form['source']
        dest = request.form['dest']
        cost = float(request.form['cost'])

    db = get_db()
    cur = db.cursor()

    # source system
    cur.execute("SELECT solarSystemID,regionID FROM eve.mapsolarsystems WHERE solarSystemName = %s" , [source] )
    source_data = cur.fetchone()
    source_data = { "name":source, "system_id":source_data[0], "region_id":source_data[1]}

    # dest system system
    cur.execute("SELECT solarSystemID,regionID FROM eve.mapsolarsystems WHERE solarSystemName = %s" , [dest] )
    dest_data = cur.fetchone()
    dest_data = {"name":dest, "system_id":dest_data[0], "region_id":dest_data[1]}

    cur.execute('''
      SELECT eve.invtypes.typeID, eve.invtypes.typeName,
      hist.vol, source.sell, (source.sell+%s*eve.invtypes.volume),
      dest.prices, dest.vols, dest.competitors,
      TIMEDIFF(UTC_TIMESTAMP(),dest.age)
      FROM eve.invtypes,
      (SELECT combined_hist.typeID as typeID, sum(combined_hist.vol) as vol FROM
        ( SELECT zk_loot.typeID AS typeID, sum(qtyDropped+qtyDestroyed)/4.0 AS vol
            FROM zk_kill
            JOIN zk_loot ON zk_kill.killID = zk_loot.killID
            WHERE zk_kill.killTime > CURDATE() - INTERVAL 30 DAY
            GROUP BY typeID
            UNION
            SELECT zk_kill.shipTypeID AS typeID, count(zk_kill.shipTypeID)/4.0 AS vol
            FROM zk_kill
            WHERE zk_kill.killTime > CURDATE() - INTERVAL 30 DAY
            GROUP BY zk_kill.shipTypeID
            ) combined_hist 
        GROUP BY combined_hist.typeID
      ) hist,
      (SELECT type_id,min(price) AS sell
        FROM market_order
        WHERE bid=0
        AND solarsystem_id=%s
        GROUP BY type_id) source LEFT OUTER JOIN
      (SELECT type_id,min(price) AS sell,max(created) AS age,
        min(price) as prices,
        sum(vol_remaining) as vols,
        count(price) as competitors
        FROM market_order
        WHERE bid=0
        AND solarsystem_id=%s
        GROUP BY type_id) dest ON source.type_id=dest.type_id
      WHERE eve.invtypes.typeID = source.type_id
      AND hist.typeID = source.type_id
      AND hist.vol*source.sell > 10000000
      AND hist.vol > 1
      AND (dest.prices/(source.sell+%s*eve.invtypes.volume)>1.25 OR dest.prices IS NULL)
      ORDER BY (source.sell+%s*eve.invtypes.volume)*0.2*hist.vol DESC ''',
      (cost,source_data["system_id"],dest_data["system_id"],cost,cost))
    data = cur.fetchmany(200)

    return render_template('import.html', title="Stock", data=data,
        source_data=source_data, dest_data=dest_data, action="stock",cost=cost)

@app.route('/export', methods=['GET', 'POST'])
def market_export():
    '''Returns a list of items to I can buy, export and sell at a profit'''
    source="K-6K16"
    dest="Jita"
    cost=275.
    if request.method == 'POST':
        source = request.form['source']
        dest = request.form['dest']
        cost = float(request.form['cost'])

    db = get_db()
    cur = db.cursor()

    # source system
    cur.execute("SELECT solarSystemID,regionID FROM eve.mapsolarsystems WHERE solarSystemName = %s" , [source] )
    source_data = cur.fetchone()
    source_data = { "name":source, "system_id":source_data[0], "region_id":source_data[1]}

    # dest system system
    cur.execute("SELECT solarSystemID,regionID FROM eve.mapsolarsystems WHERE solarSystemName = %s" , [dest] )
    dest_data = cur.fetchone()
    dest_data = {"name":dest, "system_id":dest_data[0], "region_id":dest_data[1]}

    cur.execute('''
      SELECT
      eve.invtypes.typeID, eve.invtypes.typeName,
      MAX(dest.price),
      MAX(dest.price-%s*eve.invtypes.volume),
      GROUP_CONCAT(source.price),
      GROUP_CONCAT(source.vol_remaining),
      SUM((dest.price-(source.price+%s*eve.invtypes.volume))*source.vol_remaining) as mkt_profit
      FROM eve.invtypes,
      ( SELECT type_id, max(price) AS price
        FROM market_order
        WHERE bid=1
        AND solarsystem_id=%s
        GROUP BY type_id ) dest INNER JOIN
      (SELECT type_id, price, vol_remaining
        FROM market_order
        WHERE bid=0
        AND solarsystem_id=%s
        ) source ON source.type_id=dest.type_id
      WHERE eve.invtypes.typeID = source.type_id
      AND dest.price > source.price+%s*eve.invtypes.volume
      AND eve.invtypes.marketGroupID IS NOT NULL
      GROUP BY eve.invtypes.typeID
      ORDER BY mkt_profit DESC  ''',(cost,cost,dest_data["system_id"],source_data["system_id"],cost))
    data = cur.fetchmany(1000)

    new_data = []
    for row in data:
        sell_prices = [float(x) for x in row[4].split(',')]
        sell_quants = [int(x) for x in row[5].split(',')]
        sell_orders = sorted(zip(sell_prices,sell_quants))
        new_data.append((row[0],row[1],row[2],row[3],sell_orders,row[6]))

    return render_template('export.html', title="Export", data=new_data,
        source_data=source_data, dest_data=dest_data, action="export")

@app.route('/top')
def top():
    '''Returns a list of top traded items'''
    db = get_db()
    cur = db.cursor()
    # FIXME this does not check for user id
    cur.execute(''' select eve.invtypes.typeID, eve.invtypes.typeName,
    sell.quant, sell.total, buy.quant, buy.total,
    (sell.total - buy.total) as actual_profit,
    (sell.total - buy.total*cast(sell.quant as DECIMAL)/buy.quant) as weighted_profit
    from ( select type_id, sum(quantity) as quant, sum(quantity*price) as total
           from wallet_trans
           where transaction_type='sell'
           group by type_id) as sell,
         ( select type_id, sum(quantity) as quant, sum(quantity*price) as total
           from wallet_trans
           where transaction_type='buy'
           group by type_id) as buy,
           eve.invtypes
    WHERE buy.type_id = eve.invtypes.typeID
    AND sell.type_id = eve.invtypes.typeID
    ORDER BY weighted_profit DESC ''' )
    data = cur.fetchall()

    return render_template('top.html', title="Top Items", data=data)

@app.route('/margin')
def margin():
    '''Returns a list of items in Jita with large margins'''
    db = get_db()
    cur = db.cursor()
    cur.execute(''' SELECT
      eve.invtypes.typeID,
      eve.invtypes.typeName,
      avg_hist.volume,
      avg_hist.low_price,
      avg_hist.avg_price,
      avg_hist.high_price,
      (avg_hist.high_price-avg_hist.low_price)/avg_hist.avg_price as margin,
      (avg_hist.high_price-avg_hist.low_price)*avg_hist.volume as profit
      FROM eve.invtypes,
      ( SELECT
        type_id,
        avg(avg_price) AS avg_price,
        avg(low_price) AS low_price,
        avg(high_price) AS high_price,
        sum(volume)/29 AS volume
        FROM market_hist
        WHERE region_id=10000002
        AND date > CURDATE() - INTERVAL 30 DAY
        GROUP BY type_id ) avg_hist
      WHERE avg_hist.type_id = eve.invtypes.typeID
      AND avg_hist.volume*avg_hist.avg_price>1000000
      AND (avg_hist.high_price-avg_hist.low_price)/avg_hist.avg_price >0.4
      AND (avg_hist.high_price-avg_hist.low_price)/avg_hist.avg_price <1.0
      ORDER BY profit DESC ''')

      #dest.sell_percent/(source.sell_percent+275*eve.invtypes.volume)
    data = cur.fetchmany(200)

    return render_template('margin.html', title="Margin Finder", data=data)

@app.route('/new_scan')
def new_scan():
    '''Scans through items using IGB, prioitised by lossmail-vol*price'''
    if "Eve_Regionid" in request.headers :
      db = get_db()
      cur = db.cursor()
      cur.execute('''
        SELECT kills.typeID FROM
      ( SELECT zk_loot.typeID as typeID, sum(qtyDropped+qtyDestroyed)/4.0 AS vol
        FROM zk_kill
        JOIN zk_loot ON zk_kill.killID = zk_loot.killID
        WHERE zk_kill.killTime > CURDATE() - INTERVAL 30 DAY
        GROUP BY typeID
        UNION
        SELECT zk_kill.shipTypeID, count(zk_kill.shipTypeID)/4.0 AS vol
        FROM zk_kill
        WHERE zk_kill.killTime > CURDATE() - INTERVAL 30 DAY
        GROUP BY zk_kill.shipTypeID
        ) kills
        JOIN
        ( SELECT type_id, avg(avg_price) AS price
          FROM market_hist WHERE region_id=%s
          AND date > CURDATE() - INTERVAL 30 DAY
          GROUP BY type_id ) avg_hist
        ON kills.typeID=avg_hist.type_id
        WHERE avg_hist.price*kills.vol>5000000
        ORDER BY avg_hist.price*kills.vol DESC ''',(10000002))
      data = cur.fetchall()

      return render_template('scan.html', title="Market Scanner",data=data)
    else:
      flash('IGB trust needed.','error')
      return redirect("%s/%s" % (url_for('trust'),"new_scan"))


@app.route('/old_scan')
def old_scan():
    '''Scans through items using IGB, prioitised by vol*price
    TODO, use kill mail losses to obtain volume'''
    if "Eve_Regionid" in request.headers :
      db = get_db()
      cur = db.cursor()

      cur.execute(''' SELECT avg_hist.type_id FROM
        ( SELECT type_id, avg(avg_price) AS price, sum(volume) AS vol 
          FROM market_hist WHERE region_id=%s 
          AND date > CURDATE() - INTERVAL 30 DAY  
          GROUP BY type_id ) avg_hist
        WHERE avg_hist.price*avg_hist.vol>5000000
        ORDER BY avg_hist.price*avg_hist.vol DESC ''',[request.headers["Eve_Regionid"]]) 
      data = cur.fetchall()
      return render_template('scan.html', title="Market Scanner",data=data)
    else:
      flash('IGB trust needed.','error')
      return redirect("%s/%s" % (url_for('trust'),"old_scan"))      
      
      
@app.route('/update')
@app.route('/update/<import_cost>')
def order_update(import_cost=400):
    '''Scans through items using IGB,
    shows items character currently has on market'''
    if "Eve_Charid" in request.headers :
      db = get_db()
      cur = db.cursor()

      cur.execute('''
        SELECT regionID FROM eve.mapsolarsystems
        WHERE solarSystemID = %s
      ''',(request.headers["EVE_SOLARSYSTEMID"]))
      regionID = cur.fetchone()[0]

      cur.execute('''
        SELECT
        unique_orders.type_id,
        eve.invtypes.typeName,
        stat.sell,
        stat.sell+%s*eve.invtypes.volume
        FROM eve.invtypes,
        (SELECT type_id,min(price) AS sell,max(created)
        FROM market_order
        WHERE bid=0
        AND solarsystem_id=30000142
        GROUP BY type_id) stat,
            (SELECT DISTINCT wallet_order.type_id
            FROM wallet_order
            LEFT JOIN ( SELECT stationID station, solarSystemID system from outpost
                        UNION SELECT stationID station, solarSystemID system from eve.stastations ) as station_union
            ON station_union.station = wallet_order.station_id
            JOIN eve.mapsolarsystems ON eve.mapsolarsystems.solarSystemID = station_union.system
            WHERE order_state=0
            AND eve.mapsolarsystems.regionID=%s
            AND char_id=%s) unique_orders
        WHERE unique_orders.type_id = eve.invtypes.typeID
        AND stat.type_id = unique_orders.type_id
        ''',[import_cost,regionID,request.headers["Eve_Charid"]])
      data = cur.fetchall()

      return render_template('update.html', title="Update Orders", data=data, import_cost=import_cost )
    else:
      flash('IGB trust needed.','error')
      return redirect("%s/%s" % (url_for('trust'),"order_update"))

      
@app.route('/list', methods=['GET', 'POST'])
def list_tool():
    '''tool for quickly listing items'''
    if "Eve_Charid" in request.headers :
        if request.method == 'POST':
 
            import_cost = request.form['cost']
            stuff = request.form['stuff']
            items = []
            for line in stuff.split('\n'):
                items.append(line.split('\t')[0])
            
            format_strings = ','.join(['%s'] * len(items))
            sql_params = (import_cost,) + tuple(items)
            
            db = get_db()
            cur = db.cursor()
            cur.execute('''
                SELECT
                eve.invtypes.typeID,
                eve.invtypes.typeName,
                stat.sell,
                stat.sell+%s*eve.invtypes.volume
                FROM eve.invtypes,
                (SELECT type_id,min(price) AS sell,max(created)
                    FROM market_order
                    WHERE bid=0
                    AND solarsystem_id=30000142
                    GROUP BY type_id) stat
                WHERE stat.type_id = eve.invtypes.typeID
                AND eve.invtypes.typeName IN (''' + format_strings + ''')
                ORDER BY eve.invtypes.typeName
                ''',sql_params)
            data = cur.fetchall()    
            return render_template('update.html', title="Update Orders", data=data, import_cost=import_cost )
            
        else :
            return render_template('list_tool.html', title="List Tool")#, data=data, import_cost=import_cost )
    else:
        flash('IGB trust needed.','error')
        return redirect("%s/%s" % (url_for('trust'),"list_tool"))      
      
      
@app.route('/trust')
@app.route('/trust/<redirect>')
def trust(redirect="/"):
  '''Requests trust from eve IGB'''
  # this should also act as an error page for non ingamebrowser
  return render_template('trust.html', title="Request Trust",redirect=redirect)


@app.route('/assets')
def assets():
    ''' List assets in db for this user'''
    db = get_db()
    cur = db.cursor()

    # oh god don't look at the SQL
    cur.execute('''SELECT chara.id, chara.name, asset.quantity, asset.type_id, eve.invtypes.typeName, eve.invtypes.volume, 
               asset.location_id, asset.item_id, asset.parent_id, stat.sell, asset.raw_quantity, station_un.name 
               FROM asset LEFT JOIN 
               (SELECT type_id,min(price) AS sell FROM market_order WHERE bid=0 AND solarsystem_id=30000142 GROUP BY type_id) stat 
               ON asset.type_id=stat.type_id, chara,api,user,eve.invtypes, 
               (select * from ( select stationID id, stationName name from outpost UNION select stationID id, stationName name from eve.stastations ) as test group by id ) as station_un 
               WHERE asset.type_id=eve.invtypes.typeID AND asset.location_id = station_un.id 
               AND asset.chara_id = chara.id AND chara.api_id=api.id AND api.user_id=%s 
               ORDER BY chara.id,asset.location_id,asset.parent_id,asset.item_id''',session['userid'])     
    data = cur.fetchall()

    data_test = {}
    for row in data:
        cha = row[0] # char id
        sta = row[6] # station id
        ass = row[7] # asset id

        # deal with items with no market data and BPCs
        if row[9] is None :
            pri = 0.0
        else :
            pri = float(row[9])
        if row[10]  == -2  : #This is a BPC
            pri = 0.0

        if cha not in data_test.keys(): # add character names here
            data_test[cha] = {"name":row[1],"stations":{},"total":0.0}

        if sta not in data_test[cha]["stations"].keys(): # add locations here
            data_test[cha]["stations"][sta] = {"name":row[11],"assets":{},"total":0.0}


        if row[8] is None: # not in a container
            data_test[cha]["stations"][sta]["assets"][ass] = {
                                            "name":row[4],
                                            "id":row[3],
                                            "quant":row[2],
                                            "vol":row[5],
                                            "price":pri,
                                            "contents":{}}

            # update running totals
            data_test[cha]["stations"][sta]["total"]+=pri*row[2]
            data_test[cha]["total"]+=pri*row[2]

            for contents_row in data: # loop again to find children
                # TODO this should be in a function that can be recursivly called

                # deal with items with no market data and BPCs
                if contents_row[9] is None :
                    cont_pri = 0.0
                else :
                    cont_pri = float(contents_row[9])
                if contents_row[10] == -2 : #This is a BPC
                    cont_pri = 0.0

                if contents_row[8] == ass: # child
                    data_test[cha]["stations"][sta]["assets"][ass]["contents"][contents_row[7]] = {
                                            "name":contents_row[4],
                                            "id":contents_row[3],
                                            "quant":contents_row[2],
                                            "vol":contents_row[5],
                                            "price":cont_pri,
                                            "contents":{}}
                    # update running totals
                    data_test[cha]["stations"][sta]["total"]+=cont_pri*contents_row[2]
                    data_test[cha]["total"]+=cont_pri*contents_row[2]

    return render_template('assets.html', title="Assets",data_test=data_test )

@app.route('/refine')
def refine():
    '''Returns a list of items in that can be refined at profit'''
    db = get_db()
    cur = db.cursor()
    cur.execute(''' SELECT refine.id, refine.name, refine.portion, refine.sell, market.sell*refine.portion FROM
                        (SELECT p.typeID AS id, p.typeName AS name, p.portionSize AS portion, sum(i.quantity*stat.sell) AS sell
                        FROM eve.invTypes AS p
                        JOIN eve.invTypeMaterials AS i on p.typeID=i.typeID
                        LEFT JOIN (SELECT type_id,min(price) AS sell
                            FROM market_order
                            WHERE bid=0
                            AND solarsystem_id=30000142
                            GROUP BY type_id) AS stat on i.materialTypeID=stat.type_id
                        GROUP BY p.typeID) AS refine
                    LEFT JOIN (SELECT type_id,min(price) AS sell
                        FROM market_order
                        WHERE bid=0
                        AND solarsystem_id=30000142
                        GROUP BY type_id) AS market on refine.id=market.type_id
                    WHERE refine.sell>market.sell
                    ORDER BY refine.sell/(market.sell*refine.portion) DESC
                    ''')

    data = cur.fetchall()
    return render_template('refine.html', title="Refine", data=data)

@app.route('/api/upload', methods=['POST'])
def api_upload():
    '''Recieved market orders from EMUU'''
    if request.method == 'POST':
        db = get_db()
        cur = db.cursor()
        try:
            data = json.loads(request.form["data"])
            if data["resultType"]=="orders" :
                for row in data["rowsets"] : # type id loop
                    cur.execute('''DELETE FROM market_order WHERE region_id IN (%s) AND type_id IN (%s)''' , (row["regionID"],row["typeID"]))
                    for order in row["rows"] :
                        cur.execute('''INSERT INTO market_order(bid, type_id, id, station_id, solarsystem_id, region_id, price, vol_entered,
                                    vol_remaining, min_vol, order_range, issued,expires,created) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ''',
                                    (order[6],row["typeID"],order[3],order[9],order[10],row["regionID"],order[0],order[4],order[1],order[5],order[2],
                                    order[7].replace('T',' ')[:-6],None,row["generatedAt"].replace('T',' ')[:-6]) )
                                    # hacky, to remove time zone from datetime string and 'T'
        except Exception, e:
            print "Error adding order : " + "\n" + str(e)
            return '0' 
        db.commit()
    return '1' # expected by EMUU

if __name__ == '__main__':
    app.run()
