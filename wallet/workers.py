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
    
@app.route('/tasks/transactions')
def worker_transaction():
    apis = Api.query()
    for api in apis.iter():
        for chara in api.characters: 
            # check if page will still be cached
            cache = Cache.query(Cache.api == api.key,
                                Cache.character == chara,
                                Cache.page == request.path).fetch(1)
            if cache:
                if datetime.datetime.now() < cache[0].cachedUntil + datetime.timedelta(seconds=30) :
                    continue # cached
                else :
                    cache[0].key.delete()  # cache expired
                    
            # find previous transaction 
            previousTransaction = Transaction.query().order(-Transaction.transactionID).filter(Transaction.character == chara).fetch(1,projection=[Transaction.transactionID])
            previousID = 0
            if previousTransaction:
                previousID = previousTransaction[0].transactionID
            
            # Create API object with auth and char reference
            auth = EVEAPIConnection().auth(keyID=api.keyID, vCode=api.vCode).character(chara.get().characterID)
        
            # query eve api
            try:
                WalletTransactions = auth.WalletTransactions()
            except apiError, e:
                print "eveapi returned the following error when querying transactions:"
                print "code:", e.code
                print "message:", e.message
                return
            except Exception, e:
                print "Something went horribly wrong:" + str(e)
                return
               
            # add transactions
            transactionList = []
            for transaction in WalletTransactions.transactions :
                if transaction.transactionID > previousID: 
                    t = Transaction(
                        transactionDateTime = datetime.datetime.fromtimestamp(transaction.transactionDateTime),
                        transactionID = transaction.transactionID,
                        quantity = transaction.quantity,
                        typeName = str(transaction.typeName),
                        typeID = transaction.typeID,
                        price = transaction.price,
                        #clientID = transaction.clientID,
                        #clientName =  str(transaction.clientName),
                        stationID = transaction.stationID,
                        stationName = str(transaction.stationName),
                        transactionType = transaction.transactionType,
                        #transactionFor = transaction.transactionFor,
                        #journalTransactionID = transaction.journalTransactionID,
                        character = chara,
                        user = chara.get().user
                        )
                    transactionList.append(t)
            ndb.put_multi(transactionList)
            
            # update cache
            c = Cache ( character = chara,
                        api = api.key,
                        page = request.path,
                        cachedUntil=datetime.datetime.fromtimestamp(WalletTransactions._meta.cachedUntil))
            c.put()
    return '0'
        
@app.route('/tasks/orders')
def worker_order():
    apis = Api.query()
    for api in apis.iter():
        for chara in api.characters: 
            # check if page will still be cached
            cache = Cache.query(Cache.api == api.key,
                                Cache.character == chara,
                                Cache.page == request.path).fetch(1)
            if cache:
                if datetime.datetime.now() < cache[0].cachedUntil + datetime.timedelta(seconds=30)  :
                    continue # cached
                else :
                    cache[0].key.delete()  # cache expired
        
            # Market Orders
            # Market orders api will only return orders that are active, or
            # expired/fullfilled orders that were PLACED within the last 7 days.
            # Here, I keep track of what orders have been returned then query
            # the missing orders, (Orders that were fulfilled but not recent)
            
            # get new orders
            auth = EVEAPIConnection().auth(keyID=api.keyID, vCode=api.vCode).character(chara.get().characterID)
            try:
                MarketOrders = auth.MarketOrders() 
            except apiError, e:
                print "eveapi returned the following error when querying market orders:"
                print "code: ", e.code
                print "message:", e.message
                return
            except Exception, e:
                print "Something went horribly wrong:" + str(e)
                return
               
            # get old orders,  
            previousOrders = Order.query(Order.character == chara)
            updated = []
            
            for order in MarketOrders.orders :  
                updated.append(order.orderID)
                prevOrder = previousOrders.filter(Order.orderID == order.orderID).fetch(1) 
                if prevOrder:
                    o = prevOrder[0]
                else :
                    o = Order(user = chara.get().user)
                    
                if order.orderState  == 0: # still active
                    if o.typeName == None:# add name of item if not known
                        o.typeName = Item.query(Item.typeID == order.typeID).get().typeName
                    o.orderID	  = order.orderID	
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
                    o.character   = chara
                    o.put() # I think this is fine if the item already exists, no extra writes will be made
                else : # fulfilled/cancelled/expired
                    if o.key: # if saved 
                        o.key.delete()
                    
            # find and update missing orders
            for order in previousOrders.iter():
                if not order.orderID in updated: # has the order not been updated
                    missingOrder = auth.MarketOrders(orderID=order.orderID).orders[0]
                    if missingOrder.orderState > 0:
                        order.key.delete() # order was fulfilled
                    else:
                        order.volRemaining= missingOrder.volRemaining 
                        order.price       = missingOrder.price 
                        order.issued      = datetime.datetime.fromtimestamp(missingOrder.issued)
                        
            # update cache
            c = Cache ( character = chara,
                        api = api.key,
                        page = request.path,
                        cachedUntil=datetime.datetime.fromtimestamp(MarketOrders._meta.cachedUntil))
            c.put()
    return '0'
    
   
@app.route('/tasks/assets')
def worker_asset():
    apis = Api.query()
    for api in apis.iter():
        for chara in api.characters:    
            # check if page will still be cached
            cache = Cache.query(Cache.api == api.key,
                                Cache.character == chara,
                                Cache.page == request.path).fetch(1)
            if cache:
                if datetime.datetime.now() < cache[0].cachedUntil + datetime.timedelta(seconds=30)  :
                    continue # cached
                else : # cache expired
                    cache[0].key.delete() 
    
            auth = EVEAPIConnection().auth(keyID=api.keyID, vCode=api.vCode).character(chara.get().characterID)

            # Asset list 
            try:
                AssetList = auth.AssetList()
            except apiError, e:
                print "eveapi returned the following error when querying assets:"
                print "code:", e.code
                print "message:", e.message
                return
            except Exception, e:
                print "Something went horribly wrong:" + str(e)
                return
            
            # get old items,  
            previousItems = Asset.query(Asset.character == chara)
            updated = []
            
            for asset in AssetList.assets :
                updated.append(asset.itemID)
                prevItem = previousItems.filter(Asset.itemID == asset.itemID).fetch(1) 
                if not prevItem: # item does not exist, add it
                    try: # rawQuantity attribute is weird(:ccp:), it seems only "assembled" items have it...
                        rawQuantity = asset.rawQuantity
                    except AttributeError, e: 
                        rawQuantity = None
                    a = Asset(user = chara.get().user)
                    a.itemID =asset.itemID
                    a.locationID = asset.locationID
                    a.typeID = asset.typeID
                    a.typeName = Item.query(Item.typeID == asset.typeID).get().typeName
                    a.quantity = asset.quantity 
                    a.flag = asset.flag
                    a.singleton = bool(asset.singleton)
                    a.rawQuantity = rawQuantity
                    a.character   = chara
                    a.put()
                    
                # now check for child assets inside this asset
                # this is fine for now, but we could go another order deeper. (item in container in ship for example)
                # smart thing to do is put this in a recirical function
                try: 
                    contents = asset.contents
                except AttributeError, e:  # no child assets
                    continue
                for subAsset in contents: # child assets, pass parent id and location
                    updated.append(subAsset.itemID)
                    prevItem = previousItems.filter(Asset.itemID == subAsset.itemID).fetch(1) 
                    if not prevItem:
                        try: # rawQuantity attribute is weird(:ccp:), it seems only "assembled" items have it...
                            rawQuantity = subAsset.rawQuantity
                        except AttributeError, e: 
                            rawQuantity = None
                        b = Asset(user = chara.get().user)
                        b.itemID =subAsset.itemID
                        b.locationID = asset.locationID # stacked containers have no location(:ccp:) take location of parent
                        b.typeID = subAsset.typeID
                        b.typeName = Item.query(Item.typeID == subAsset.typeID).get().typeName
                        b.quantity = subAsset.quantity 
                        b.flag = subAsset.flag
                        b.singleton = bool(subAsset.singleton)
                        b.rawQuantity = rawQuantity
                        b.character   = chara
                        b.put()
                
            # remove missing items
            for asset in previousItems.iter():
                if not asset.itemID in updated: # old item was not found
                    asset.key.delete() 

            # update cache
            c = Cache ( character = chara,
                        api = api.key,
                        page = request.path,
                        cachedUntil=datetime.datetime.fromtimestamp(AssetList._meta.cachedUntil))
            c.put()
    return '0'
    
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
    
   
    
    
    
    
    
    
    
    
    
