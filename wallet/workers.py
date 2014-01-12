from wallet import app
from models import Api,Character,Transaction,Order,Cache,Asset,Item

from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.api import taskqueue
from google.appengine.datastore.datastore_query import Cursor

from flask import request

from eveapi import EVEAPIConnection
from eveapi import Error as apiError

import json
import urllib2
import datetime
    
# TODO add docstrings to all these functions

# TODO optimise with async puts

@app.route('/tasks/api')
def worker_api():
    tasks = [update_balance, update_transactions, update_orders, update_assets]
    for apiEntity in Api.query():
        for charKey in apiEntity.characters: 
        
            # Character item
            charEntity = charKey.get()
             # eve api connection
            auth = EVEAPIConnection().auth(keyID=apiEntity.keyID, vCode=apiEntity.vCode).character(charEntity.characterID)
            
            for task in tasks:
                # check if page will still be cached
                cache = Cache.query(Cache.api == apiEntity.key,
                                    Cache.character == charKey,
                                    Cache.page == task.__name__).get()
                if cache:
                    if datetime.datetime.now() < cache.cachedUntil + datetime.timedelta(seconds=30)  :
                        continue   # cached
                    else :  # cache expired
                        cache.key.delete()  
                cachedUntil = task(auth,charEntity)
                c = Cache ( character = charKey,
                            api = apiEntity.key,
                            page = task.__name__,
                            cachedUntil=cachedUntil)
                c.put()
    return '0'

def update_balance(auth,charEntity):
    try:
        accountBalance = auth.AccountBalance() 
    except api_error, e:
        logging.error("eveapi returned the following error when querying account balance: %s, %s", e.code, e.message)
        return 0
    except Exception, e:
        logging.error("Something went horribly wrong: %s", str(e))
        return 0
            
    # update wallet
    charEntity.wallet = accountBalance.accounts[0].balance # Characters only have 1 account, (corps?)
    charEntity.put()
    return datetime.datetime.fromtimestamp(accountBalance._meta.cachedUntil)

def update_transactions(auth,charEntity):
    try:
        walletTransactions = auth.WalletTransactions()
    except api_error, e:
        logging.error("eveapi returned the following error when querying wallet transactions: %s, %s", e.code, e.message)
        return 0
    except Exception, e:
        logging.error("Something went horribly wrong: %s", str(e))
        return 0
                    
    # find previous transaction 
    # TODO, think about this some more
    previousTransaction = Transaction.query()
    previousTransaction = previousTransaction.order(-Transaction.transactionID)
    previousTransaction = previousTransaction.filter(Transaction.character == charEntity.key)
    previousTransaction = previousTransaction.fetch(1,projection=[Transaction.transactionID])
    
    previousID = 0
    if previousTransaction:
        previousID = previousTransaction[0].transactionID

    # add transactions
    transactionList = []
    for transaction in walletTransactions.transactions :
        if transaction.transactionID > previousID: 
            itemEntity = Item.query(Item.typeID == transaction.typeID).get()
            t = Transaction(
                transactionDateTime = datetime.datetime.fromtimestamp(transaction.transactionDateTime),
                transactionID = transaction.transactionID,
                quantity = transaction.quantity,
                typeName = str(transaction.typeName),
                typeID = transaction.typeID,
                price = transaction.price,
                stationID = transaction.stationID,
                stationName = str(transaction.stationName),
                transactionType = transaction.transactionType,
                itemKey = itemEntity.key,
                character = charEntity.key,
                user = charEntity.user
                )
            transactionList.append(t)
    ndb.put_multi(transactionList)

    return datetime.datetime.fromtimestamp(walletTransactions._meta.cachedUntil)


def update_orders(auth,charEntity):
    try:
        marketOrders = auth.MarketOrders()
    except api_error, e:
        logging.error("eveapi returned the following error when querying market orders: %s, %s", e.code, e.message)
        return 0
    except Exception, e:
        logging.error("Something went horribly wrong: %s", str(e))
        return 0         
        
    # get old orders,  
    previousOrders = Order.query(Order.character == charEntity.key)
    
    # keep track of what I update
    updated = []
    
    # running total on orders
    buy = 0.0;
    sell = 0.0;

    # orders returned by api
    for order in marketOrders.orders :  
        updated.append(order.orderID)
        prevOrder = previousOrders.filter(Order.orderID == order.orderID).get()
        if prevOrder:
            o = prevOrder  # existing order
        else :
            o = Order(user = charEntity.user)  # new order

        if order.orderState  == 0: # still active
            if o.typeName == None:# add name of item if not known
                o.typeName = Item.query(Item.typeID == order.typeID).get().typeName
            o.orderID     = order.orderID
            o.charID      = order.charID
            o.stationID   = order.stationID 
            o.volEntered  = order.volEntered 
            o.volRemaining= order.volRemaining 
            o.typeID      = order.typeID 
            o.duration    = order.duration 
            o.escrow      = order.escrow 
            o.price       = order.price 
            o.bid         = bool(order.bid)
            o.issued      = datetime.datetime.fromtimestamp(order.issued)
            o.character   = charEntity.key
            o.put() #  I think this is fine if the item already exists, no extra writes will be made
            if bool(order.bid):
                buy += order.volRemaining * order.price 
            else:
                sell += order.volRemaining * order.price 
        else : # fulfilled/cancelled/expired
            if o.key: # if saved 
                o.key.delete()

    # find and update orders missing from api
    for order in previousOrders:
        if not order.orderID in updated: # has the order not been updated
            missingOrder = auth.marketOrders(orderID=order.orderID).orders[0]
            if missingOrder.orderState > 0:
                order.key.delete() # order was fulfilled
            else:
                order.volRemaining= missingOrder.volRemaining 
                order.price       = missingOrder.price 
                order.issued      = datetime.datetime.fromtimestamp(missingOrder.issued)
                if bool(missingOrder.price .bid):
                    buy += missingOrder.price.volRemaining * missingOrder.price.price 
                else:
                    sell += missingOrder.price.volRemaining * missingOrder.price.price 

    # update wallet
    charEntity.sell = sell
    charEntity.buy = buy
    charEntity.put()   
                
    return datetime.datetime.fromtimestamp(marketOrders._meta.cachedUntil)
    
def add_asset(charEntity,previousItems,container,updated):
    assetWorth = 0.0
    
    for asset in container :
        updated.append(asset.itemID)
        prevItem = previousItems.filter(Asset.itemID == asset.itemID).get() # TODO turn in to class method
        itemEntity = Item.query(Item.typeID == asset.typeID).get()
        # rawQuantity attribute is weird(:ccp:), 
        # it seems only "assembled" items have it...
        try: 
            rawQuantity = asset.rawQuantity
        except AttributeError, e: 
            rawQuantity = None
        
        if prevItem: 
            prevItem.itemKey = itemEntity.key
            prevItem.put()
        else: 
            a = Asset(user = charEntity.user)
            a.itemKey = itemEntity.key
            a.itemID = asset.itemID
            a.locationID = asset.locationID
            a.typeID = asset.typeID
            a.typeName = itemEntity.typeName
            a.quantity = asset.quantity 
            a.flag = asset.flag
            a.singleton = bool(asset.singleton)
            a.rawQuantity = rawQuantity
            a.character = charEntity.key
            a.put()
        if rawQuantity is None or rawQuantity > -2: # not a bpc
            assetWorth += itemEntity.sell*asset.quantity 
    
    # now check for child assets inside this asset
    try: 
        contents = asset.contents
    except AttributeError, e:  # no child assets
        return assetWorth 
    else:  # add child assets
        return assetWorth + add_asset(charEntity,previousItems,contents,updated)

def update_assets(auth,charEntity):
    try:
        assetList = auth.AssetList()
    except api_error, e:
        logging.error("eveapi returned the following error when querying asset list: %s, %s", e.code, e.message)
        return 0
    except Exception, e:
        logging.error("Something went horribly wrong: %s", str(e))
        return 0    
        
    # keep track of what items I've seen and updated
    updated = []
            
    # and what items are already added
    previousItems = Asset.query(Asset.character == charEntity.key)
    
    # add assets to db and keep running total on assets worth
    assetWorth = add_asset(charEntity,previousItems,assetList.assets,updated)
    
    # remove missing items (sold, destroyed, moved etc)
    for asset in previousItems:
        if not asset.itemID in updated: # old item was not found
            asset.key.delete() 
    
    # update wallet
    charEntity.assets = assetWorth
    charEntity.put()
    
    return datetime.datetime.fromtimestamp(assetList._meta.cachedUntil)
        
@app.route('/tasks/prices', methods=['GET', 'POST'])
def worker_prices():
    url = 'http://api.eve-marketdata.com/api/item_prices2.json?char_name=scruff_decima&region_ids=10000002&buysell=s&type_ids='
    
    # add typeIDs to url depending on how this is called
    if request.method == 'GET':# first called from app engine cron job
        items, nextCurs, more = Item.query().fetch_page(100)
    
    elif request.method == 'POST':# task queue, 
        if request.form.get("cur"): # cursur for next page of results of typeid
            curs = Cursor(urlsafe=request.form.get('cur'))
            items, nextCurs, more = Item.query().fetch_page(100,start_cursor=curs)
        else:
            print "Error: no cursor"
            return '0'# something wrong
     
    typeIDs = []
    for item in items:
        typeIDs.append(str(item.typeID))
    url += ','.join(typeIDs)
       
    try: 
        response = urllib2.urlopen(url)
    except Exception, e:
        print "Error retieving url : " + str(url) + "\n" + str(e)
        return
         
    data = response.read() 
    parsedData = json.loads(data)
    result = parsedData["emd"]["result"]
    itemList = []

    for row in result:
        a = row["row"]
        typeID = int(a["typeID"])
        
        for item in items:
            if item.typeID == typeID:
                item.sell = float(a["price"])
                itemList.append(item)
    ndb.put_multi(itemList)

    if more and nextCurs:
        # if we have more to fetch append it to task queue
        taskqueue.add(url='/tasks/prices', params={'cur':  nextCurs.urlsafe()})
    
    
    return '0'

    
    
    
    
    
    
    
    
    
