import eveapi
import functools
import time

from app import db, celery
from .models import Corporation, Character, Api, Transaction

ROWCOUNT = 500

# TODO, cache?

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
    #TODO corp or character transactions?
    this_api = db.session.query(Api).get(kwargs['keyID'])
    auth = eveapi.EVEAPIConnection().auth(keyID=kwargs['keyID'],
                                          vCode=kwargs['vCode'])
    if this_api.type == 'Corporation':
        corporationID = this_api.corporations[0].corporationID
        auth = auth.corp
        extra_kwargs={'this_api':this_api,
                      'auth':auth,
                      'corporationID':corporationID}
        kwargs.update(extra_kwargs)
        return _transactions_corp(**kwargs)
    else:
        characterID = kwargs['characterID']
        auth = auth.character(characterID)
        extra_kwargs={'this_api':this_api,
                      'auth':auth,
                      'characterID':characterID}
        kwargs.update(extra_kwargs)
        return _transactions_char(**kwargs)

@api_requirements(access_mask=4194304, allowed_types=['Character','Account'])
def _transactions_char(**kwargs):
    fromID = 0  # seems to work
    new = None
    transaction_list=[]
    while new is None or new>0:
        new = 0
        walletTransactions = kwargs['auth'].WalletTransactions(rowCount=ROWCOUNT,
                                                               fromID=fromID)
        for t in walletTransactions.transactions :
            if Transaction.get_by(transactionID=t.transactionID) is None:
                transaction = Transaction(transactionID=t.transactionID)
                transaction.populate_from_object(t)
                transaction.characterID=kwargs['characterID']
                new+=1
                print t.transactionID
                transaction_list.append(transaction)
            fromID = t.transactionID if fromID == 0 else min(t.transactionID,fromID)
        time.sleep(1)
    db.session.add_all(transaction_list)
    db.session.commit()

@api_requirements(access_mask=2097152, allowed_types=['Corporation'])
def _transactions_corp(**kwargs):
    fromID = 0  # seems to work
    new = None
    transaction_list=[]
    while new is None or new>0:
        new = 0
        walletTransactions = kwargs['auth'].WalletTransactions(rowCount=ROWCOUNT,
                                                               fromID=fromID)
        for t in walletTransactions.transactions :
            if Transaction.get_by(transactionID=t.transactionID) is None:
                transaction = Transaction(transactionID=t.transactionID)
                transaction.populate_from_object(t)
                transaction.corporationID=kwargs['corporationID']
                new+=1
                print t.transactionID
                transaction_list.append(transaction)
            fromID = t.transactionID if fromID == 0 else min(t.transactionID,fromID)
        time.sleep(1)
    db.session.add_all(transaction_list)
    db.session.commit()
