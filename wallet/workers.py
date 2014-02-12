from wallet import app,db
import decorators
import models

from eveapi import EVEAPIConnection
from eveapi import Error as apiError

# import json
# import urllib2
import datetime
import logging

ROWCOUNT = 200


# TODO add docstrings to all these functions

        
@app.route('/tasks/api')
def worker_api():
    #tasks = [update_balance, update_transactions, update_orders, update_assets]
    tasks = [update_orders]
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
    except Exception, e:
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
    
# def add_asset(charEntity,previousItems,container,updated):
    # assetWorth = 0.0
    
    # for asset in container :
        # updated.append(asset.itemID)
        # prevItem = previousItems.filter(Asset.itemID == asset.itemID).get() # TODO turn in to class method
        # itemEntity = Item.query(Item.typeID == asset.typeID).get()
        # # rawQuantity attribute is weird(:ccp:), 
        # # it seems only "assembled" items have it...
        # try: 
            # rawQuantity = asset.rawQuantity
        # except AttributeError, e: 
            # rawQuantity = None
        
        # if prevItem: 
            # prevItem.itemKey = itemEntity.key
            # prevItem.put()
        # else: 
            # a = Asset(user = charEntity.user)
            # a.itemKey = itemEntity.key
            # a.itemID = asset.itemID
            # a.locationID = asset.locationID
            # a.typeID = asset.typeID
            # a.typeName = itemEntity.typeName
            # a.quantity = asset.quantity 
            # a.flag = asset.flag
            # a.singleton = bool(asset.singleton)
            # a.rawQuantity = rawQuantity
            # a.character = charEntity.key  # add 'owner' field ?
            # a.put()
        # if rawQuantity is None or rawQuantity > -2: # not a bpc
            # assetWorth += itemEntity.sell*asset.quantity 
    
    # # now check for child assets inside this asset
    # try: 
        # contents = asset.contents
    # except AttributeError, e:  # no child assets
        # return assetWorth 
    # else:  # add child assets
        # return assetWorth + add_asset(charEntity,previousItems,contents,updated)

# def update_assets(auth,charEntity):
    # try:
        # assetList = auth.AssetList()
    # except apiError, e:
        # logging.error("eveapi returned the following error when querying asset list: %s, %s", e.code, e.message)
        # return 
    # except Exception, e:
        # logging.error("Something went horribly wrong: %s", str(e))
        # return
        
    # # keep track of what items I've seen and updated
    # updated = []
            
    # # and what items are already added
    # previousItems = Asset.query(Asset.character == charEntity.key)  # add 'owner' field ?
    
    # # add assets to db and keep running total on assets worth
    # assetWorth = add_asset(charEntity,previousItems,assetList.assets,updated)
    
    # # remove missing items (sold, destroyed, moved etc)
    # for asset in previousItems:
        # if not asset.itemID in updated: # old item was not found
            # asset.key.delete() 
    
    # # update wallet
    # charEntity.assets = assetWorth
    # charEntity.put()
    
    # return datetime.datetime.fromtimestamp(assetList._meta.cachedUntil)
        
# @app.route('/tasks/prices', methods=['GET', 'POST'])
# def worker_prices():
    # url = 'http://api.eve-marketdata.com/api/item_prices2.json?char_name=scruff_decima&region_ids=10000002&buysell=s&type_ids='
    
    # # add typeIDs to url depending on how this is called
    # if request.method == 'GET':# first called from app engine cron job
        # items, nextCurs, more = Item.query().fetch_page(100)
    
    # elif request.method == 'POST':# task queue, 
        # if request.form.get("cur"): # cursur for next page of results of typeid
            # curs = Cursor(urlsafe=request.form.get('cur'))
            # items, nextCurs, more = Item.query().fetch_page(100,start_cursor=curs)
        # else:
            # print "Error: no cursor"
            # return '0'# something wrong
     
    # typeIDs = []
    # for item in items:
        # typeIDs.append(str(item.typeID))
    # url += ','.join(typeIDs)
       
    # try: 
        # response = urllib2.urlopen(url)
    # except Exception, e:
        # print "Error retieving url : " + str(url) + "\n" + str(e)
        # return
         
    # data = response.read() 
    # parsedData = json.loads(data)
    # result = parsedData["emd"]["result"]
    # itemList = []

    # for row in result:
        # a = row["row"]
        # typeID = int(a["typeID"])
        
        # for item in items:
            # if item.typeID == typeID:
                # item.sell = float(a["price"])
                # itemList.append(item)
    # ndb.put_multi(itemList)

    # if more and nextCurs:
        # # if we have more to fetch append it to task queue
        # taskqueue.add(url='/tasks/prices', params={'cur':  nextCurs.urlsafe()})
    
    
    # return '0'

    
    
    
    
    
    
    
    
    
