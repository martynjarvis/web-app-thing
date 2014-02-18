from evewallet.webapp import app,db,decorators,models

from evewallet.eveapi import EVEAPIConnection
from evewallet.eveapi import Error as apiError

import json
import urllib2
import datetime
import logging

ROWCOUNT = 200
MARKETROWCOUNT = 5000
# TODO add docstrings to all these functions
        
@app.route('/tasks/api')
def worker_api():
    tasks = [update_balance, update_transactions, update_orders, update_assets]
    for api in db.session.query(models.Api).all():
        if api.corporation is not None: 
            auth = EVEAPIConnection().auth(keyID=api.id, vCode=api.vCode).corp
            for task in tasks:
                task(auth=auth,entity=api.corporation)                 
                db.session.flush()  # TODO catch exceptions here
        else:
            for character in api.characters: 
                auth = EVEAPIConnection().auth(keyID=api.id, vCode=api.vCode).character(character.id)
                for task in tasks:
                    task(auth=auth,entity=character)
                    db.session.flush()
    db.session.commit()            
    return '0'

@decorators.cache
def update_balance(auth,entity):
    try:
        accountBalance = auth.AccountBalance() 
    except apiError, e:
        logging.error("eveapi returned the following error when querying account balance: %s, %s", e.code, e.message)
        return 
    except Exception , e:
        logging.error("Something went horribly wrong: %s", str(e))
        return 
        
    # update wallet
    entity.balance = accountBalance.accounts[0].balance # Characters only have 1 account, (corps?)
    return datetime.datetime.fromtimestamp(accountBalance._meta.cachedUntil)

@decorators.cache
def update_transactions(auth,entity):
    transaction_list = []
    retVal = None
    
    fromId = 0  # seems to work
    new = ROWCOUNT
    while new>0:
        new = 0
        try:
            walletTransactions = auth.WalletTransactions(rowCount=ROWCOUNT, fromID=fromId)
        except apiError, e:
            logging.error("eveapi returned the following error when querying wallet transactions: %s, %s", e.code, e.message)
            return
        except Exception, e:
            logging.error("Something went horribly wrong: %s", str(e))
            return
            
        for transaction in walletTransactions.transactions :
            if not models.Transaction.inDB(transaction.transactionID):
                transaction_list.append(models.Transaction(transaction,entity))
                new+=1
            fromId = transaction.transactionID
        retVal = datetime.datetime.fromtimestamp(walletTransactions._meta.cachedUntil)
    
    db.session.add_all(transaction_list)
    return retVal

@decorators.cache
def update_orders(auth,entity):
    order_list = []
    
    try:
        marketOrders = auth.MarketOrders()
    except apiError, e:
        logging.error("eveapi returned the following error when querying market orders: %s, %s", e.code, e.message)
        return 
    except Exception, e:
        logging.error("Something went horribly wrong: %s", str(e))
        return   

    updated = []

    # orders returned by api
    for order in marketOrders.orders :    
        thisOrder = models.Order.getByID(order.orderID)
        if thisOrder is None:
            order_list.append(models.Order(order,entity))
        else:
            thisOrder.update(order,entity)
            updated.append(order.orderID)

    for order in models.Order.getMissingOrders(entity,updated):
        order.update(auth.marketOrders(orderID=order.id).orders[0],entity)
        
    db.session.add_all(order_list)   
    return datetime.datetime.fromtimestamp(marketOrders._meta.cachedUntil)
    
def add_asset(entity,container,updated):
    asset_list = []
    for asset in container :

        updated.append(asset.itemID)
        if not models.Asset.inDB(asset.itemID):
            asset_list.append(models.Asset(asset,entity))  
        # now check for child assets inside this asset
        try: 
            contents = asset.contents
        except AttributeError, e:  # no child assets
            pass  
        else:  # add child assets
            add_asset(entity,contents,updated)
    db.session.add_all(asset_list)  

@decorators.cache    
def update_assets(auth,entity):
    try:
        assetList = auth.AssetList()
    except apiError, e:
        logging.error("eveapi returned the following error when querying asset list: %s, %s", e.code, e.message)
        return 
    except Exception, e:
        logging.error("Something went horribly wrong: %s", str(e))
        return

    # keep track of what items I've seen and updated
    updated = []
    add_asset(entity,assetList.assets,updated)
    db.session.flush() 
    
    # remove missing items (sold, destroyed, moved etc)
    for asset in entity.assets:
        if not asset.id in updated: # old item was not found
            db.session.delete(asset)
    
    return datetime.datetime.fromtimestamp(assetList._meta.cachedUntil)
        
@app.route('/tasks/prices')
def worker_prices():
    url = 'http://api.eve-marketdata.com/api/item_prices2.json?char_name=scruff_decima&solarsystem_ids={systems}&buysell=a&type_ids={types}'
    
    types = db.session.query(models.InvTypes).filter(models.InvTypes.marketGroupID is not None).filter(models.InvTypes.marketGroupID < 300000).all()

    system_list = [30003862,30003794,30003830,30000142]
    systems = ','.join([str(x) for x in system_list]) #agil, stacmon, orvole, jita
    
    typesPerQuery = MARKETROWCOUNT/(2*len(system_list))
    
    i = 0
    while i<len(types):
        print i, len(types)
        typesIDs = ','.join([str(type.typeID) for type in types[i:i+typesPerQuery]])

        i+=typesPerQuery

        try: 
            response = urllib2.urlopen(url.format(systems=systems,types=typesIDs))
        except urllib2.URLError, e:
            logging.error("Error retieving url : " + str(url) + "\n" + str(e))
            return '0'
             
        data = response.read() 
        parsedData = json.loads(data)
        result = parsedData["emd"]["result"]

        for row in result:
            models.ItemPrice.update(row['row'])
            
        db.session.flush()
        
    db.session.commit()            
    return '0'
             
@app.route('/tasks/history')
def worker_history():
    url = 'http://api.eve-marketdata.com/api/item_history2.json?char_name=scruff_decima&region_ids={regions}&type_ids={types}'
    types = db.session.query(models.InvTypes).filter(models.InvTypes.marketGroupID is not None).filter(models.InvTypes.marketGroupID < 300000).all()

    region_list = [10000049,10000048,10000002]
    regions = ','.join([str(x) for x in region_list]) #   khanid, placid, forge
    
    typesPerQuery = MARKETROWCOUNT/(30*len(region_list))
    
    i = 0
    while i<len(types):
        print i, len(types)
        typesIDs = ','.join([str(type.typeID) for type in types[i:i+typesPerQuery]])

        i+=typesPerQuery

        try: 
            response = urllib2.urlopen(url.format(regions=regions,types=typesIDs))
        except urllib2.URLError, e:
            logging.error("Error retieving url : " + str(url) + "\n" + str(e))
            return '0'
             
        data = response.read() 
        parsedData = json.loads(data)
        result = parsedData["emd"]["result"]

        for row in result:
            models.ItemHistory.update(row['row'])
            
        db.session.flush()
        
    db.session.commit()            
    return '0'
    
    
    
    
    
