import eveapi
import functools
import time

from app import db, celery
from .models import Corporation, Character, Api, Transaction, Order

ROWCOUNT = 500

# TODO, cache

def api_requirements(access_mask=None, allowed_types=None):
    def decorator(method):
        @functools.wraps(method)
        def f(**kwargs):
            this_api = kwargs.get('this_api', None) or db.session.query(Api).get(kwargs['keyID'])
            if (access_mask is None) or ((this_api.accessMask & access_mask) > 1):
                if (allowed_types is None) or (this_api.type in allowed_types):
                    method(**kwargs)
                    return True
            return False
        return f
    return decorator

@celery.task()
def character_sheet(**kwargs):
    return _character_sheet(**kwargs)

@api_requirements(access_mask=8, allowed_types=['Account', 'Character'])
def _character_sheet(keyID, vCode, characterID):
    auth = eveapi.EVEAPIConnection().auth(keyID=keyID, vCode=vCode)
    sheet = auth.character(characterID).CharacterSheet()
    character = Character.get_or_create(characterID=characterID)
    character.populate_from_object(sheet)
    db.session.commit()

@celery.task()
def corporation_sheet(**kwargs):
    return _corporation_sheet(**kwargs)

@api_requirements(access_mask=8, allowed_types=['Corporation'])
def _corporation_sheet(**kwargs):
    if 'keyID' in kwargs:
        auth = eveapi.EVEAPIConnection().auth(keyID=kwargs['keyID'],
                                              vCode=kwargs['vCode'])
        sheet = auth.corp.CorporationSheet()
    elif 'characterID' in kwargs:
        # TODO, Can't currently reach this due to decorator...
        auth = eveapi.EVEAPIConnection()
        sheet = auth.corp.CorporationSheet(characterID=kwargs['characterID'])
    else:
        raise KeyError
    corporation = Corporation.get_or_create(corporationID=sheet.corporationID)
    corporation.populate_from_object(sheet)
    db.session.commit()

@celery.task()
def transactions(**kwargs):
    this_api = db.session.query(Api).get(kwargs['keyID'])
    kwargs.update({'this_api': this_api}) # keep hold of api object
    if this_api.type == 'Corporation':
        return _transactions_corp(**kwargs)
    else:
        return _transactions_char(**kwargs)

@api_requirements(access_mask=2097152, allowed_types=['Corporation'])
def _transactions_corp(**kwargs):
    auth = eveapi.EVEAPIConnection().auth(keyID=kwargs['keyID'],
                                          vCode=kwargs['vCode'])
    corp_auth = auth.corp
    corporation = kwargs['this_api'].corporations[0]
    _update_transactions(corp_auth, corporationID=corporation.corporationID)

@api_requirements(access_mask=4194304, allowed_types=['Character','Account'])
def _transactions_char(**kwargs):
    auth = eveapi.EVEAPIConnection().auth(keyID=kwargs['keyID'],
                                          vCode=kwargs['vCode'])
    char_auth = auth.character(kwargs['characterID'])
    character = Character.get_by(characterID=kwargs['characterID'])
    _update_transactions(char_auth, characterID=character.characterID)

def _update_transactions(auth, corporationID=None, characterID=None):
    fromID = 0  # seems to work
    new = None
    transaction_list=[]
    while new is None or new>0:
        new = 0
        walletTransactions = auth.WalletTransactions(rowCount=ROWCOUNT,
                                                     fromID=fromID)
        for t in walletTransactions.transactions :
            if Transaction.get_by(transactionID=t.transactionID) is None:
                transaction = Transaction(transactionID=t.transactionID)
                transaction.populate_from_object(t)
                if corporationID:
                    transaction.corporationID=corporationID
                if characterID:
                    transaction.characterID=characterID
                new+=1
                transaction_list.append(transaction)
            fromID = t.transactionID if fromID == 0 else min(t.transactionID,fromID)
        time.sleep(1)
    db.session.add_all(transaction_list)
    db.session.commit()

@celery.task()
def orders(**kwargs):
    this_api = db.session.query(Api).get(kwargs['keyID'])
    kwargs.update({'this_api': this_api}) # keep hold of api object
    if this_api.type == 'Corporation':
        return _orders_corp(**kwargs)
    else:
        return _orders_char(**kwargs)

@api_requirements(access_mask=4096, allowed_types=['Corporation'])
def _orders_corp(**kwargs):
    auth = eveapi.EVEAPIConnection().auth(keyID=kwargs['keyID'],
                                          vCode=kwargs['vCode'])
    corporationID = kwargs['this_api'].corporations[0].corporationID
    active_orders = db.session.query(Order).filter_by(corporationID=corporationID,
                                                      orderState=0).all()
    _update_orders(auth.corp, active_orders, corporationID)

@api_requirements(access_mask=4096, allowed_types=['Character','Account'])
def _orders_char(**kwargs):
    auth = eveapi.EVEAPIConnection().auth(keyID=kwargs['keyID'],
                                          vCode=kwargs['vCode'])
    characterID = kwargs['characterID']
    active_orders = db.session.query(Order).filter_by(charID=characterID,
                                                      orderState=0).all()
    _update_orders(auth.character(characterID), active_orders)

def _update_orders(auth, order_list, corporationID=None):
    updated_orders = []
    marketOrders = auth.MarketOrders()
    for api_order in marketOrders.orders:
        db_order = Order.get_or_create(orderID=api_order.orderID)
        db_order.populate_from_object(api_order)
        if corporationID:
            db_order.corporationID=corporationID
        updated_orders.append(api_order.orderID)

    for old_order in order_list:
        if old_order.orderID not in updated_orders:
            api_order = auth.marketOrders(orderID=old_order.orderID).orders[0]
            old_order.populate_from_object(api_order)
    db.session.commit()

