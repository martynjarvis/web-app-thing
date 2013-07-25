from wallet import app
from models import Api,Character,Transaction

from google.appengine.ext import ndb

from eveapi import EVEAPIConnection
from eveapi import Error as api_error

import datetime
    
@app.route('/tasks/transactions')
def worker_transaction():
    apis = Api.query()
    for api in apis.iter():
        for chara in api.characters: 
            previousTransaction = Transaction.query(Transaction.character == chara).order(-Transaction.transactionID).fetch(1)
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
                        clientID = transaction.clientID,
                        clientName =  str(transaction.clientName),
                        stationID = transaction.stationID,
                        stationName = str(transaction.stationName),
                        transactionType = transaction.transactionType,
                        transactionFor = transaction.transactionFor,
                        journalTransactionID = transaction.journalTransactionID,
                        character = chara
                        )
                    transactionList.append(t)
            ndb.put_multi(transactionList)
    return '0'
    