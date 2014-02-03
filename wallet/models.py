from wallet import db

APITYPES = {'Account':1, 'Character':2, 'Corporation':3}
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

class Character(db.Model):
    __tablename__ = 'Character'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    corporationID = db.Column(db.Integer)
    corporationName = db.Column(db.String(80))
    balance = db.Column(db.Float)
    
    def __init__(self,id,name):
        self.id = int(id)
        self.name = name
        
   
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

    
# def test_api(auth):

    # except api_error, e:
        # flash('API related error','error')
        # return
    # except Exception, e:
        # flash('unknown error','error')
        # return
    # return APIKeyInfo.key.type 
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
    
    


    
# class Transaction(ndb.Model):
    # itemKey = ndb.KeyProperty(Item)
    # transactionDateTime=ndb.DateTimeProperty(indexed=False)
    # transactionID=ndb.IntegerProperty()
    # quantity=ndb.IntegerProperty(indexed=False)
    # typeName=ndb.StringProperty(indexed=False)
    # typeID=ndb.IntegerProperty()
    # price=ndb.FloatProperty(indexed=False)
    # #clientID=ndb.IntegerProperty()#
    # #clientName=ndb.StringProperty()#
    # stationID=ndb.IntegerProperty(indexed=False)
    # stationName=ndb.StringProperty(indexed=False)
    # transactionType=ndb.StringProperty(indexed=False)
    # #transactionFor=ndb.StringProperty()#
    # #journalTransactionID=ndb.IntegerProperty()#
    # character = ndb.KeyProperty(Character)
    # user = ndb.UserProperty(required = True)
    
# class Order(ndb.Model):
    # itemKey = ndb.KeyProperty(Item)
    # orderID	= ndb.IntegerProperty()
    # charID	= ndb.IntegerProperty()
    # charName	= ndb.StringProperty(indexed=False)
    # stationID = ndb.IntegerProperty(indexed=False)
    # # ? stationName=ndb.StringProperty(indexed=False)
    # # ? region?
    # volEntered = ndb.IntegerProperty(indexed=False)
    # volRemaining = ndb.IntegerProperty(indexed=False)
    # #minVolume = ndb.IntegerProperty()
    # #orderState = ndb.IntegerProperty()
    # typeID = ndb.IntegerProperty()
    # typeName=ndb.StringProperty(indexed=False)
    # #range = ndb.IntegerProperty()
    # #accountKey = ndb.IntegerProperty()
    # duration = ndb.IntegerProperty(indexed=False)
    # escrow = ndb.FloatProperty(indexed=False)
    # price = ndb.FloatProperty(indexed=False)
    # bid = ndb.BooleanProperty(indexed=False)
    # issued = ndb.DateTimeProperty(indexed=False)
    # owner = ndb.KeyProperty()
    # user = ndb.UserProperty(required = True)

    
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
    

