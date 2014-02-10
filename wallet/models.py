from wallet import db
from sqlalchemy.sql import exists

APITYPES = {'Account':1, 'Character':2, 'Corporation':3}
TRANSACTIONTYPE = {'buy':1, 'sell':2}
TRANSACTIONFOR = {'personal':1, 'corporation':2}
DTPATTERN = '%Y-%m-%d %H:%M:%S'
import eveapi
import datetime
import hashlib 
#from eveapi import EVEAPIConnection, Error

class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    hash = db.Column(db.String(80))
    
    apis = db.relationship("Api", backref="user")

    def __init__(self, username, email, password):
        self.username = username
        self.email = email           
        self.hash = hashlib.sha1(password).hexdigest()

    def __repr__(self):
        return '<User %r>' % self.username
    
    @classmethod
    def get(cls,id):
        return db.session.query(User).filter(User.id==id).first()

    @classmethod
    def auth(cls,username,password):
        hash = hashlib.sha1(password).hexdigest()
        return db.session.query(User).filter(User.username==username).filter(User.hash==hash).first()

api_char = db.Table('api_char', db.metadata,
    db.Column('api_id', db.Integer, db.ForeignKey('Api.id')),
    db.Column('char_id', db.Integer, db.ForeignKey('Character.id'))
)
   
class Api(db.Model):
    __tablename__ = 'Api'
    id = db.Column(db.Integer, primary_key=True)
    vCode = db.Column(db.String(80))
    type = db.Column(db.Integer)
    accessMask = db.Column(db.Integer)
    expires = db.Column(db.DateTime)
    userId = db.Column(db.Integer, db.ForeignKey('User.id'))
    
    characters = db.relationship("Character",
                    secondary=api_char,
                    backref="apis")
    
    def __init__(self,id,vCode,userId):
        self.id = int(id)
        self.vCode = vCode
        self.userId = int(userId)
    
    def update(self):
        auth = eveapi.EVEAPIConnection().auth(keyID=self.id, vCode=self.vCode)
        
        # fill api information
        try: 
            APIKeyInfo = auth.account.APIKeyInfo()
        except eveapi.Error, e:
            return 1
        except Exception, e:
            return 2
        self.type = APITYPES[APIKeyInfo.key.type]
        self.accessMask = int(APIKeyInfo.key.accessMask)
        try:
            self.expires = datetime.datetime.strptime(APIKeyInfo.key.expires,DTPATTERN)
        except ValueError:
            self.expires = None
        
        #fill character information    #TODO corporations   
        self.characters=[]
        for row in APIKeyInfo.key.characters:
            character = db.session.query(User).filter(Character.id==row.characterID).first()
            if character is None:
                character = Character(row.characterID,row.characterName)
            self.characters.append(character)  
        return 0
        
# def update_corp_from_api(auth):
    # charList = []
    # corporationSheet = auth.corp.CorporationSheet()
    # q = Corporation.query().filter(Corporation.corporationID == corporationSheet.corporationID).get()
    # if q:
        # c = q
    # else :
        # c = Corporation()
    # c.user = users.get_current_user()
    # c.corporationID=int(corporationSheet.corporationID)
    # c.corporationName=corporationSheet.corporationName
    # c.ticker=corporationSheet.ticker
    # c.put()
    # return c.key   
        
class Character(db.Model):
    __tablename__ = 'Character'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    corporationID = db.Column(db.Integer)
    corporationName = db.Column(db.String(80))
    balance = db.Column(db.Float)
    
    transactions = db.relationship("Transaction", backref="character")
    orders = db.relationship("Order", backref="character")
    
    def __init__(self,id,name):
        self.id = int(id)
        self.name = name
        
# class Corporation(ndb.Model):
    # corporationID=ndb.IntegerProperty()
    # corporationName=ndb.StringProperty(indexed=False)
    # ticker=ndb.StringProperty(indexed=False)
    # user = ndb.UserProperty(required = True)
    # wallet = ndb.FloatProperty(indexed=False)
    # sell = ndb.FloatProperty(indexed=False)
    # buy = ndb.FloatProperty(indexed=False)
    # assets = ndb.FloatProperty(indexed=False)
    # def name(self):
        # return self.corporationName

class Cache(db.Model): # keeps track of what needs to be updated
    __tablename__ = 'Cache'
    key = db.Column(db.String(80), primary_key=True)
    page = db.Column(db.String(80), primary_key=True)
    cachedUntil=db.Column(db.DateTime)
    def __init__(self,key,page):
        self.key = key
        self.page = page
        self.cachedUntil = None
  
    @classmethod
    def get(cls,key,page):
        return db.session.query(Cache).filter(Cache.key==key).filter(Cache.page==page).first()


class Transaction(db.Model):
    __tablename__ = 'Transaction'
    id = db.Column(db.Integer, primary_key=True)
    transactionDateTime = db.Column(db.DateTime)
    quantity = db.Column(db.Integer)
    typeName = db.Column(db.String(80))
    typeID = db.Column(db.Integer)
    price = db.Column(db.Float)
    clientID = db.Column(db.Integer)
    clientName = db.Column(db.String(80))
    stationID = db.Column(db.Integer)
    stationName = db.Column(db.String(80))
    transactionType = db.Column(db.Integer)
    transactionFor = db.Column(db.Integer)
    journalTransactionID = db.Column(db.BigInteger)
    
    charID = db.Column(db.Integer, db.ForeignKey('Character.id'))
    
    def __init__(self,transaction,char):
        self.id = int(transaction.transactionID)
        self.transactionDateTime = datetime.datetime.fromtimestamp(transaction.transactionDateTime)
        self.quantity = int(transaction.quantity)
        self.typeName = str(transaction.typeName)
        self.typeID = int(transaction.typeID)
        self.price = float(transaction.price)
        self.clientID  = int(transaction.clientID)
        self.clientName = str(transaction.clientName)
        self.stationID = int(transaction.stationID)
        self.stationName = str(transaction.stationName)
        self.transactionType = TRANSACTIONTYPE[transaction.transactionType]
        self.transactionFor = TRANSACTIONFOR[transaction.transactionFor]
        self.journalTransactionID = transaction.journalTransactionID
        self.charID = char.id
        
    @classmethod
    def inDB(cls,id):
        return db.session.query(exists().where(Transaction.id == id)).scalar()
    
        
class Order(db.Model):
    __tablename__ = 'Order'
    id = db.Column(db.Integer, primary_key=True)
    stationID = db.Column(db.Integer)
    volEntered = db.Column(db.Integer)
    volRemaining = db.Column(db.Integer)
    minVolume = db.Column(db.Integer)
    orderState = db.Column(db.Integer) #Valid states: 0 = open/active, 1 = closed, 2 = expired (or fulfilled), 3 = cancelled, 4 = pending, 5 = character deleted. 
    typeID = db.Column(db.Integer)
    range = db.Column(db.Integer)
    accountKey = db.Column(db.Integer) # Always 1000 for characters, but in the range 1000 to 1006 for corporations.
    duration = db.Column(db.Integer)# How many days this order is good for. Expiration is issued + duration in days.
    escrow = db.Column(db.Float)
    price = db.Column(db.Float)
    bid = db.Column(db.Boolean)
    issued = db.Column(db.DateTime)
    charID = db.Column(db.Integer, db.ForeignKey('Character.id')) # could cause problems if char is in corp, but no API
    
    def __init__(self,order,char):
        self.id = order.orderID
        self.stationID = order.stationID
        self.volEntered = order.volEntered
        self.volRemaining = order.volRemaining
        self.minVolume = order.minVolume
        self.orderState = order.orderState
        self.typeID = order.typeID
        self.range = order.range
        self.accountKey = order.accountKey
        self.duration = order.duration
        self.escrow = order.escrow
        self.price = order.price
        self.bid = order.bid
        self.issued = datetime.datetime.fromtimestamp(order.issued)
        self.charID = char.id   
        
    def update(self,order,char):
        self.volRemaining = order.volRemaining
        self.orderState = order.orderState
        self.duration = order.duration
        self.escrow = order.escrow
        self.price = order.price
        self.issued = datetime.datetime.fromtimestamp(order.issued)
        
    @classmethod
    def getByID(cls,id):
        return db.session.query(Order).filter(Order.id==id).first()
        
    @classmethod
    def getMissingOrders(cls,char,updated):
        retVal = []
        for order in char.orders:
            if order.id not in updated:
                retVal.append(order)
        return retVal
        
        
# class Item(ndb.Model):
    # typeID = ndb.IntegerProperty()
    # typeName=ndb.StringProperty()
    # volume=ndb.FloatProperty(indexed=False)
    # marketGroupID = ndb.IntegerProperty()
    # buy = ndb.FloatProperty(indexed=False)
    # sell = ndb.FloatProperty(indexed=False)

# class MarketStat(ndb.Model):
    # typeID = ndb.IntegerProperty()
    # volume = ndb.IntegerProperty(indexed=False)
    # avg = ndb.FloatProperty(indexed=False)
    # max = ndb.FloatProperty(indexed=False)
    # min = ndb.FloatProperty(indexed=False)
    # stddev = ndb.FloatProperty(indexed=False)
    # median = ndb.FloatProperty(indexed=False)
    # percentile = ndb.FloatProperty(indexed=False)
    # retreived=ndb.DateTimeProperty(indexed=False)




    


    

    
# class Asset(ndb.Model):
    # itemKey = ndb.KeyProperty(Item)
    # itemID = ndb.IntegerProperty()
    # locationID = ndb.IntegerProperty(indexed=False)
    # typeID = ndb.IntegerProperty()
    # typeName=ndb.StringProperty(indexed=False)
    # quantity = ndb.IntegerProperty(indexed=False)
    # flag = ndb.IntegerProperty(indexed=False)
    # singleton = ndb.BooleanProperty(indexed=False)
    # rawQuantity = ndb.IntegerProperty(indexed=False)
    # character = ndb.KeyProperty(Character)
    # user = ndb.UserProperty(required = True)
    

