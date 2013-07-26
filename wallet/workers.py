from wallet import app
from models import Api,Character,Transaction,Order

from google.appengine.ext import ndb
from google.appengine.api import users

from eveapi import EVEAPIConnection
from eveapi import Error as api_error

import datetime
    
@app.route('/tasks/transactions')
def worker_transaction():
    apis = Api.query()
    for api in apis.iter():
        for chara in api.characters: 
            previousTransaction = Transaction.query().order(-Transaction.transactionID).filter(Transaction.character == chara).fetch(1,projection=[Transaction.transactionID])
            previousID = 0
            if previousTransaction:
                previousID = previousTransaction[0].transactionID
            
            # Create API object with auth and char reference
            auth = EVEAPIConnection().auth(keyID=api.keyID, vCode=api.vCode).character(chara.get().characterID)
        
            # Wallet balances
            try:
                wallet_transactions = auth.WalletTransactions()
            except api_error, e:
                print "eveapi returned the following error when querying transactions:"
                print "code:", e.code
                print "message:", e.message
                return
            except Exception, e:
                print "Something went horribly wrong:" + str(e)
                return
                
            transactionList = []
            for transaction in wallet_transactions.transactions :
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
    return '0'
        
@app.route('/tasks/orders')
def worker_order():
    apis = Api.query()
    for api in apis.iter():
        for chara in api.characters: 
            # Market Orders
            # Market orders api will only return orders that are active, or
            # expired/fullfilled orders that were PLACED within the last 7 days.
            # Here, I keep track of what orders have been returned then query
            # the missing orders, (Orders that were fulfilled but not recent)
            
            # get new orders
            auth = EVEAPIConnection().auth(keyID=api.keyID, vCode=api.vCode).character(chara.get().characterID)
            try:
                wallet_orders = auth.MarketOrders() 
            except api_error, e:
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
            
            for order in wallet_orders.orders :  
                updated.append(order.orderID)
                prevOrder = previousOrders.filter(Order.orderID == order.orderID).fetch(1) # the filter is probably the problem here
                if prevOrder:
                    o = prevOrder[0]
                else :
                    o = Order(user = chara.get().user)
                    
                if order.orderState  == 0: # still active
                    o.orderID	  = order.orderID	
                    #o.charID      = order.charID
                    o.stationID   = order.stationID 
                    o.volEntered  = order.volEntered 
                    o.volRemaining= order.volRemaining 
                    #o.minVolume   = order.minVolume 
                    #o.orderState  = order.orderState 
                    o.typeID      = order.typeID 
                    #o.range       = order.range 
                    #o.accountKey  = order.accountKey 
                    o.duration    = order.duration 
                    o.escrow      = order.escrow 
                    o.price       = order.price 
                    o.bid         = bool(order.bid)
                    o.issued      = datetime.datetime.fromtimestamp(order.issued)
                    o.character   = chara
                    o.put()
                else : # fulfilled/cancelled/expired
                    if o.key: # if saved 
                        o.key.delete()
                    
            # find and update missing orders
            for order in previousOrders.iter():
                if not order.orderID in updated: # has the order not been updated
                    missingOrder = auth.MarketOrders(orderID=order.orderID)  
                    if missingOrder.orderState > 0:
                        order.key.delete() # order was fulfilled
                    else:
                        order.volRemaining= missingOrder.volRemaining 
                        order.price       = missingOrder.price 
                        order.issued      = datetime.datetime.fromtimestamp(missingOrder.issued)

    return '0'
    
 
    