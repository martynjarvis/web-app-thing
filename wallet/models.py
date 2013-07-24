from google.appengine.ext import ndb

class User(ndb.Model):
    """
    Universal user model. Can be used with App Engine's default users API,
    own auth or third party authentication methods (OpenID, OAuth etc).
    based on https://gist.github.com/kylefinley
    """
    #: Creation date.
    created = ndb.DateTimeProperty(auto_now_add=True)
    #: Modification date.
    updated = ndb.DateTimeProperty(auto_now=True)
    #: User defined unique name, also used as key_name.
    # Not used by OpenID
    username = ndb.StringProperty()
    #: User Name
    name = ndb.StringProperty()
    #: User Last Name
    last_name = ndb.StringProperty()
    #: User email
    email = ndb.StringProperty()
    #: Hashed password. Only set for own authentication.
    # Not required because third party authentication
    # doesn't use password.
    password = ndb.StringProperty()
    #: User Country
    country = ndb.StringProperty()
    #: User TimeZone
    tz = ndb.StringProperty()
    #: Account activation verifies email
    activated = ndb.BooleanProperty(default=False)
    
    @classmethod
    def _get_by_email(cls, email):
        return cls.query(cls.email == email).get()
        
    @classmethod
    def _get_by_username(cls, username):
        return cls.query(cls.username == username).get()
    


class Api(ndb.Model):
    keyID = ndb.IntegerProperty()
    vCode = ndb.StringProperty()
    characters = ndb.IntegerProperty(repeated = True)
    user = ndb.KeyProperty(kind=User)
    
class Character(ndb.Model):
    characterID=ndb.IntegerProperty()
    characterName=ndb.StringProperty()
    corporationID=ndb.IntegerProperty()
    corporationName=ndb.StringProperty()
    user = ndb.KeyProperty(kind=User)
    
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
    