from google.appengine.ext import ndb
from google.appengine.api import users

class Character(ndb.Model):
    characterID=ndb.IntegerProperty()
    characterName=ndb.StringProperty()
    corporationID=ndb.IntegerProperty()
    corporationName=ndb.StringProperty()
    user = ndb.UserProperty(required = True)

class Api(ndb.Model):
    keyID = ndb.IntegerProperty()
    vCode = ndb.StringProperty()
    characters = ndb.KeyProperty(kind=Character,repeated = True)
    user = ndb.UserProperty(required = True)
    
    
class Transaction(ndb.Model):
    transactionDateTime=ndb.DateTimeProperty()
    transactionID=ndb.IntegerProperty()
    quantity=ndb.IntegerProperty()
    typeName=ndb.StringProperty()
    typeID=ndb.IntegerProperty()
    price=ndb.FloatProperty()
    clientID=ndb.IntegerProperty()
    clientName=ndb.StringProperty()
    stationID=ndb.IntegerProperty()
    stationName=ndb.StringProperty()
    transactionType=ndb.StringProperty()
    transactionFor=ndb.StringProperty()
    journalTransactionID=ndb.IntegerProperty()
    character = ndb.KeyProperty(Character)
    user = ndb.UserProperty(required = True)
    
class Order(ndb.Model):
    orderID	= ndb.IntegerProperty()
    charID	= ndb.IntegerProperty()
    stationID = ndb.IntegerProperty()
    volEntered = ndb.IntegerProperty()
    volRemaining = ndb.IntegerProperty()
    minVolume = ndb.IntegerProperty()
    orderState = ndb.IntegerProperty()
    typeID = ndb.IntegerProperty()
    range = ndb.IntegerProperty()
    accountKey = ndb.IntegerProperty()
    duration = ndb.IntegerProperty()
    escrow = ndb.FloatProperty()
    price = ndb.FloatProperty()
    bid = ndb.BooleanProperty()
    issued = ndb.DateTimeProperty()
    character = ndb.KeyProperty(Character)
    user = ndb.UserProperty(required = True)