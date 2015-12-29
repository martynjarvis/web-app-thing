# -*- coding: utf-8 -*-

import datetime
import pymysql 

from lib.eveapi import EVEAPIConnection
from lib.eveapi import Error as api_error


def get_db():
    return pymysql.connect(host="localhost",port=3306,user="test",passwd="pleaseignore",db="wallet")

def fetch_all():        
    print 'Updating all from eve api.'
    db = get_db()
    cur = db.cursor()
    
    cur.execute("SELECT api.id,api.vcode,chara.id FROM api,chara WHERE api.id=chara.api_id")
    
    for api_id,api_vcode,chara_id in cur.fetchall() :
         
        # Create API object with auth and char reference
        auth = EVEAPIConnection().auth(keyID=api_id, vCode=api_vcode).character(chara_id)
        
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

        for transaction in wallet_transactions.transactions :
            cur.execute(''' insert into wallet_trans(char_id, transaction_time,\
                id, quantity, type_name, type_id, price, client_id,\
                client_name, station_id, station_name, transaction_type,\
                transaction_for, journal_id) values\
                (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) on duplicate key\
                update id=id''', 
                [chara_id, 
                datetime.datetime.fromtimestamp(transaction.transactionDateTime).strftime('%Y-%m-%d %H:%M:%S'),
                transaction.transactionID,
                transaction.quantity,
                transaction.typeName, 
                transaction.typeID,
                transaction.price, 
                transaction.clientID,
                transaction.clientName, 
                transaction.stationID,
                transaction.stationName, 
                transaction.transactionType,
                transaction.transactionFor,
                transaction.journalTransactionID] )
        
        # Market Orders
        # Market orders api will only return orders that are active, or
        # expired/fullfilled orders that were PLACED within the last 7 days.
        # Here, I keep track of what orders have been returned then query
        # the missing orders, (Orders that were fulfilled but not recent)
        cur.execute('''SELECT id FROM wallet_order 
                       WHERE order_state=0
                       AND char_id=%s''',[chara_id])

        current_orders = cur.fetchall()
        current_orders = list(order[0] for order in current_orders)
        
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
           
        for order in wallet_orders.orders :     
            if order.orderID in current_orders:
                current_orders.remove(order.orderID)
            cur.execute(''' insert into wallet_order( char_id, id,\
                station_id, vol_entered, vol_remaining, min_vol,\
                order_state, type_id, order_range, account, duration,\
                escrow, price, bid, issued) values\
                (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) on duplicate\
                key update vol_remaining=%s, order_state=%s, price=%s, issued=%s''', 
                [chara_id, 
                order.orderID,
                order.stationID,
                order.volEntered,
                order.volRemaining,
                order.minVolume,
                order.orderState,
                order.typeID,
                order.range,
                order.accountKey,
                order.duration,
                order.escrow,
                order.price,
                order.bid,
                datetime.datetime.fromtimestamp(order.issued).strftime('%Y-%m-%d %H:%M:%S'),
                order.volRemaining,
                order.orderState,
                order.price,
                datetime.datetime.fromtimestamp(order.issued).strftime('%Y-%m-%d %H:%M:%S')
                ] )
        for order_id in current_orders :
            print "fetching missing order: ", str(order_id)
            missing_order = auth.MarketOrders(orderID=order_id)     
            for order in missing_order.orders:
                cur.execute(''' UPDATE wallet_order 
                SET vol_remaining=%s, 
                    order_state=%s, 
                    price=%s,
                    issued=%s
                WHERE id=%s''', 
                [ order.volRemaining,
                  order.orderState,
                  order.price,
                  datetime.datetime.fromtimestamp(
                      order.issued).strftime(
                          '%Y-%m-%d %H:%M:%S'),
                  order.orderID, ] )
         
        # Wallet balances
        try:
            account_balance = auth.AccountBalance() 
        except api_error, e:
            print "eveapi returned the following error when querying account balance:"
            print "code:", e.code
            print "message:", e.message
            return
        except Exception, e:
            print "Something went horribly wrong:", str(e)
            return
        
        for account in account_balance.accounts :
            cur.execute(''' insert into balance ( char_id, id, account_key,
            balance) values (%s, %s, %s, %s) on duplicate key update
            balance=%s ''', 
            [chara_id, account.accountID, account.accountKey, 
             account.balance, account.balance])
        
        # Asset list 
        try:
            asset_list = auth.AssetList()
        except api_error, e:
            print "eveapi returned the following error when querying assets:"
            print "code:", e.code
            print "message:", e.message
            return
        except Exception, e:
            print "Something went horribly wrong:" + str(e)
            return
        #clear assest list here    
        cur.execute('''DELETE FROM asset WHERE chara_id = %s''',(chara_id) )
        for asset in asset_list.assets :
            asset_parser(chara_id,cur,asset)
        
    db.commit()

    # update wallet history
    cur.execute("SELECT user.id FROM user")
    users = cur.fetchall()
    for user_id in users:

        cur.execute('''SELECT chara.name, balance.balance 
            FROM balance,chara,api,user\
            WHERE balance.char_id = chara.id \
            AND chara.api_id=api.id \
            AND api.user_id=%s''',[user_id]);
        wallet_data = cur.fetchall()

        cur.execute('''SELECT chara.name, \
            SUM(wallet_order.price*wallet_order.vol_remaining) \
            FROM wallet_order,chara,api,user\
            WHERE wallet_order.bid=0 \
            AND wallet_order.order_state=0 \
            AND wallet_order.char_id=chara.id \
            AND chara.api_id=api.id \
            AND api.user_id=%s 
            GROUP BY wallet_order.char_id''',[user_id]);
        sell_data = cur.fetchall()

        cur.execute('''SELECT chara.name, \
            SUM(wallet_order.escrow) \
            FROM wallet_order,chara,api,user\
            WHERE wallet_order.bid=1 \
            AND wallet_order.order_state=0 \
            AND wallet_order.char_id=chara.id \
            AND chara.api_id=api.id \
            AND api.user_id=%s 
            GROUP BY wallet_order.char_id''',[user_id]);
        buy_data = cur.fetchall()
        
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
            GROUP BY chara.id''',[user_id])
        asset_data = cur.fetchall()

        #print(user_id,wallet_data,sell_data,buy_data)
        #print asset_data
        liquid = 0
        sell_orders = 0
        buy_orders = 0
        assets = 0
        for x,balance in wallet_data :
            liquid+=balance      
        for x,balance in sell_data :
            sell_orders+=balance        
        for x,balance in buy_data :
            buy_orders+=balance
        for x,balance in asset_data :
            assets+=balance
        
        cur.execute(''' INSERT into wallet_hist ( user_id, query_time, 
                        sell_orders, buy_orders,liquid, assets)
                        values (%s,UTC_TIMESTAMP(), %s, %s, %s, %s)''', 
                        [user_id, sell_orders, buy_orders, liquid, assets])

    db.commit()
    db.close()
    print 'Updating all from eve api. - DONE'
    
    
    
def asset_parser(chara,cur,asset,parent_id=None,parent_location=None):
    ''' this is recursivley called to account for stacked containers'''
    
    # stacked containers have no location(:ccp:), inherit location from parent
    try: 
        location = asset.locationID
    except AttributeError, e: # no contents
        location = parent_location   

        
    # rawQuantity attribute is weird(:ccp:), it seems only "assembled" items have it...
    ###Items in the AssetList (and ContractItems) now include a rawQuantity attribute if the quantity in the DB is negative. 
    ###Negative quantities are in fact codes, -1 indicates that the item is a singleton (non-stackable). If the item happens
    ###to be a Blueprint, -1 is an Original and -2 is a Blueprint Copy. 
    try: 
        raw_quantity = asset.rawQuantity
    except AttributeError, e: 
        raw_quantity = None
        
    cur.execute(''' insert into asset(chara_id,item_id, parent_id, location_id, type_id, quantity, flag, singleton, raw_quantity)
    values(%s,%s,%s,%s,%s,%s,%s,%s,%s)''', 
    [chara,asset.itemID,parent_id,location,asset.typeID,asset.quantity,asset.flag,asset.singleton,raw_quantity] )
    
    # check for child assets inside this asset
    try: 
        contents = asset.contents
    except AttributeError, e:  # no child assets
        return
    for sub_asset in contents: # child assets, pass parent id and location
        asset_parser(chara,cur,sub_asset,asset.itemID,location)

          
if __name__ == '__main__':
    fetch_all()
