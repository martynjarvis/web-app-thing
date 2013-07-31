from google.appengine.ext import ndb
from google.appengine.api import users

class Character(ndb.Model):
    characterID=ndb.IntegerProperty()
    characterName=ndb.StringProperty(indexed=False)
    #corporationID=ndb.IntegerProperty()
    #corporationName=ndb.StringProperty()
    user = ndb.UserProperty(required = True)

class Api(ndb.Model):
    keyID = ndb.IntegerProperty()
    vCode = ndb.StringProperty(indexed=False)
    characters = ndb.KeyProperty(kind=Character,repeated = True,indexed=False)
    user = ndb.UserProperty(required = True)
    
class Cache(ndb.Model): # keeps track of what needs to be updated
    character = ndb.KeyProperty(kind=Character)
    api = ndb.KeyProperty(kind=Api)
    page = ndb.StringProperty()
    cachedUntil=ndb.DateTimeProperty(indexed=False)
    
class Transaction(ndb.Model):
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
    orderID	= ndb.IntegerProperty()
    #charID	= ndb.IntegerProperty()
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
    character = ndb.KeyProperty(Character)
    user = ndb.UserProperty(required = True)
    
class Asset(ndb.Model):
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


    # think de normalised
    # typeID, typeVolume, jitaVol, jitaSell, jitaBuy, karanVol,karanSell,karanBuy
    
class Item(ndb.Model):
    typeID = ndb.IntegerProperty()
    typeName=ndb.StringProperty()
    volume=ndb.FloatProperty(indexed=False)
    marketGroupID = ndb.IntegerProperty()
    
    
    
    