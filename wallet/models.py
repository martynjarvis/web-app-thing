from google.appengine.ext import ndb
from google.appengine.api import users

import datetime
# TODO: need consistency between type and item (change item class to type)
    
class Item(ndb.Model):
    typeID = ndb.IntegerProperty()
    typeName=ndb.StringProperty()
    volume=ndb.FloatProperty(indexed=False)
    marketGroupID = ndb.IntegerProperty()
    buy = ndb.FloatProperty(indexed=False)
    sell = ndb.FloatProperty(indexed=False)
    
class Character(ndb.Model):
    characterID=ndb.IntegerProperty()
    characterName=ndb.StringProperty(indexed=False)
    user = ndb.UserProperty(required = True)
    wallet = ndb.FloatProperty(indexed=False)
    sell = ndb.FloatProperty(indexed=False)
    buy = ndb.FloatProperty(indexed=False)
    assets = ndb.FloatProperty(indexed=False)
    def name(self):
        return self.characterName

class Corporation(ndb.Model):
    corporationID=ndb.IntegerProperty()
    corporationName=ndb.StringProperty(indexed=False)
    ticker=ndb.StringProperty(indexed=False)
    user = ndb.UserProperty(required = True)
    wallet = ndb.FloatProperty(indexed=False)
    sell = ndb.FloatProperty(indexed=False)
    buy = ndb.FloatProperty(indexed=False)
    assets = ndb.FloatProperty(indexed=False)
    def name(self):
        return self.corporationName
    
    
class Api(ndb.Model):
    keyID = ndb.IntegerProperty()
    vCode = ndb.StringProperty(indexed=False)
    type = ndb.StringProperty(indexed=False)
    characters = ndb.KeyProperty(kind=Character,repeated = True,indexed=False)
    corporation = ndb.KeyProperty(kind=Corporation,indexed=False)
    user = ndb.UserProperty(required = True)
    
class Cache(ndb.Model): # keeps track of what needs to be updated
    entityKey = ndb.KeyProperty()
    page = ndb.StringProperty()
    cachedUntil=ndb.DateTimeProperty(indexed=False)
    @classmethod
    def run(cls,task,auth,entity):
        cache = Cache.query(Cache.entityKey == entity.key,Cache.page == task.__name__).get()
        if cache:
            if (cache.cachedUntil) and datetime.datetime.now() < cache.cachedUntil + datetime.timedelta(seconds=30)  :
                return  # cached
            else :  # cache expired
                cache.key.delete()  
        cachedUntil = task(auth,entity)
        c = Cache ( entityKey = entity.key,
                    page = task.__name__,
                    cachedUntil=cachedUntil)
        c.put()
        
    # TODO do cache searching and updating here
    
class Transaction(ndb.Model):
    itemKey = ndb.KeyProperty(Item)
    transactionDateTime=ndb.DateTimeProperty(indexed=False)
    transactionID=ndb.IntegerProperty()
    quantity=ndb.IntegerProperty(indexed=False)
    typeName=ndb.StringProperty(indexed=False)
    typeID=ndb.IntegerProperty()
    price=ndb.FloatProperty(indexed=False)
    #clientID=ndb.IntegerProperty()#
    #clientName=ndb.StringProperty()#
    stationID=ndb.IntegerProperty(indexed=False)
    stationName=ndb.StringProperty(indexed=False)
    transactionType=ndb.StringProperty(indexed=False)
    #transactionFor=ndb.StringProperty()#
    #journalTransactionID=ndb.IntegerProperty()#
    character = ndb.KeyProperty(Character)
    user = ndb.UserProperty(required = True)
    
class Order(ndb.Model):
    itemKey = ndb.KeyProperty(Item)
    orderID	= ndb.IntegerProperty()
    charID	= ndb.IntegerProperty()
    charName	= ndb.StringProperty(indexed=False)
    stationID = ndb.IntegerProperty(indexed=False)
    # ? stationName=ndb.StringProperty(indexed=False)
    # ? region?
    volEntered = ndb.IntegerProperty(indexed=False)
    volRemaining = ndb.IntegerProperty(indexed=False)
    #minVolume = ndb.IntegerProperty()
    #orderState = ndb.IntegerProperty()
    typeID = ndb.IntegerProperty()
    typeName=ndb.StringProperty(indexed=False)
    #range = ndb.IntegerProperty()
    #accountKey = ndb.IntegerProperty()
    duration = ndb.IntegerProperty(indexed=False)
    escrow = ndb.FloatProperty(indexed=False)
    price = ndb.FloatProperty(indexed=False)
    bid = ndb.BooleanProperty(indexed=False)
    issued = ndb.DateTimeProperty(indexed=False)
    owner = ndb.KeyProperty()
    user = ndb.UserProperty(required = True)

    
class Asset(ndb.Model):
    itemKey = ndb.KeyProperty(Item)
    itemID = ndb.IntegerProperty()
    locationID = ndb.IntegerProperty(indexed=False)
    typeID = ndb.IntegerProperty()
    typeName=ndb.StringProperty(indexed=False)
    quantity = ndb.IntegerProperty(indexed=False)
    flag = ndb.IntegerProperty(indexed=False)
    singleton = ndb.BooleanProperty(indexed=False)
    rawQuantity = ndb.IntegerProperty(indexed=False)
    character = ndb.KeyProperty(Character)
    user = ndb.UserProperty(required = True)
    

