from evewallet.webapp import db

#from sqlalchemy.sql import exists
import datetime

BUY = 1
SELL = 2

TRANSACTIONTYPE = {'buy':BUY, 'sell':SELL}
MKTTRANSTYPE = {'b':BUY, 's':SELL}
TRANSACTIONFOR = {'personal':1, 'corporation':2}
DTPATTERN = '%Y-%m-%d %H:%M:%S'
JITA = 30000142

ACTIVITY_NAMES = {  1: 'Manufacturing',
                    2: 'Researching Technology',
                    3: 'Researching Time Productivity',
                    4: 'Researching Material Productivity',
                    5: 'Copying',
                    6: 'Duplicating ',
                    7: 'Reverse Engineering ',
                    8: 'Invention'}
# Eve data
class TypeID(db.Model):
    __tablename__ = 'TypeID'
    id = db.Column(db.Integer, primary_key=True)
    graphic_id = db.Column(db.Integer)
    radius = db.Column(db.Float)
    sound_id = db.Column(db.Integer)
    icon_id = db.Column(db.Integer)
    faction_id = db.Column(db.Integer)
    volume = db.Column(db.Float)# I need to hack this in
    name = db.Column(db.String(80))# I need to hack this in

class Blueprint(db.Model):
    __tablename__ = 'Blueprint'
    id = db.Column(db.Integer, primary_key=True)
    production_limit = db.Column(db.Integer, nullable=False)

class Activity(db.Model):
    __tablename__ = 'Activity'
    id = db.Column(db.Integer, primary_key=True)
    blueprint_id = db.Column(db.Integer, db.ForeignKey('Blueprint.id'), nullable=False)
    type = db.Column(db.Integer, nullable=False)
    time = db.Column(db.Integer, nullable=False)

    blueprint = db.relationship("Blueprint", backref="activities")

    def type_string(self):
        return ACTIVITY_NAMES[self.type]

class Material(db.Model):
    __tablename__ = 'Material'
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('Activity.id'), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('TypeID.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    consume = db.Column(db.Boolean, nullable=False)

    activity = db.relationship("Activity", backref="materials")
    type = db.relationship("TypeID")

class Product(db.Model):
    __tablename__ = 'Product'
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('Activity.id'), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('TypeID.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    probability = db.Column(db.Float)

    activity = db.relationship("Activity", backref="products")
    type = db.relationship("TypeID")

# My data

class Api(db.Model):
    __tablename__ = 'Api'
    id = db.Column(db.Integer, primary_key=True)
    vcode = db.Column(db.String(80))
    type = db.Column(db.Integer)
    access_mask = db.Column(db.Integer)
    expires = db.Column(db.DateTime)
    type = db.Column(db.Integer)

    character_id = db.Column(db.Integer, db.ForeignKey('Character.id'))
    corporation_id = db.Column(db.Integer, db.ForeignKey('Corporation.id'))

    character = db.relationship("Character", backref="api_keys")
    corporation = db.relationship("Corporation", backref="api_keys")

class Character(db.Model):
    __tablename__ = 'Character'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    corporationID = db.Column(db.Integer)
    corporationName = db.Column(db.String(80))

class Corporation(db.Model):
    __tablename__ = 'Corporation'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    ticker = db.Column(db.String(5), unique=True)

class Project(db.Model):
    __tablename__ = 'Project'
    id = db.Column(db.Integer, primary_key=True)
    output_id = db.Column(db.Integer, db.ForeignKey('TypeID.id'), nullable=False)
    output_quantity = db.Column(db.Integer)

    output = db.relationship("TypeID")
    tasks = db.relationship("Task", cascade="all,delete", backref="project")
    raw_materials = db.relationship("RawMaterial", cascade="all,delete", backref="project")

class Task(db.Model):
    __tablename__ = 'Task'
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('Activity.id'), nullable=False)
    output_id = db.Column(db.Integer, db.ForeignKey('TypeID.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('Project.id'), nullable=False)
    parent_task_id = db.Column(db.Integer, db.ForeignKey('Task.id'))
    state = db.Column(db.Integer)
    output_quantity = db.Column(db.Integer)

    activity = db.relationship("Activity")
    output = db.relationship("TypeID")
    parent = db.relationship("Task", remote_side=[id], backref="children")

class RawMaterial(db.Model):
    __tablename__ = 'RawMaterial'
    id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer, db.ForeignKey('TypeID.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('Project.id'), nullable=False)
    parent_task_id = db.Column(db.Integer, db.ForeignKey('Task.id'))
    state = db.Column(db.Integer)
    quantity = db.Column(db.Integer)

    type = db.relationship("TypeID")
    task = db.relationship("Task", backref="raw_materials")



# class Cache(db.Model): # keeps track of what needs to be updated
    # __tablename__ = 'Cache'
    # key = db.Column(db.String(80), primary_key=True)
    # page = db.Column(db.String(80), primary_key=True)
    # cachedUntil=db.Column(db.DateTime)
    # def __init__(self,key,page):
        # self.key = key
        # self.page = page
        # self.cachedUntil = None

    # @classmethod
    # def get(cls,key,page):  #TODO this is not needed (see sqlalchemy get method)
        # return db.session.query(Cache).filter(Cache.key==key).filter(Cache.page==page).first()


# class Transaction(db.Model):
    # __tablename__ = 'Transaction'
    # id = db.Column(db.BigInteger, primary_key=True)
    # transactionDateTime = db.Column(db.DateTime)
    # quantity = db.Column(db.Integer)
    # price = db.Column(db.Float)
    # clientID = db.Column(db.Integer)
    # clientName = db.Column(db.String(80))
    # transactionType = db.Column(db.Integer)
    # transactionFor = db.Column(db.Integer)
    # journalTransactionID = db.Column(db.BigInteger)

    # charID = db.Column(db.Integer, db.ForeignKey('Character.id'))
    # corpID = db.Column(db.Integer, db.ForeignKey('Corporation.id'))

    # typeName = db.Column(db.String(80))
    # typeID = db.Column(db.Integer, db.ForeignKey('invtypes.typeID'))
    # type = db.relationship(InvTypes)

    # stationName = db.Column(db.String(80))
    # stationID = db.Column(db.Integer, db.ForeignKey('stastations.stationID'))
    # station = db.relationship(StaStations)

    # def __init__(self,transaction,entity):
        # self.id = int(transaction.transactionID)
        # self.transactionDateTime = datetime.datetime.fromtimestamp(transaction.transactionDateTime)
        # self.quantity = int(transaction.quantity)
        # self.typeName = str(transaction.typeName)
        # self.typeID = int(transaction.typeID)
        # self.price = float(transaction.price)
        # self.clientID  = int(transaction.clientID)
        # self.clientName = str(transaction.clientName)
        # self.stationID = int(transaction.stationID)
        # self.stationName = str(transaction.stationName)
        # self.transactionType = TRANSACTIONTYPE[transaction.transactionType]
        # self.transactionFor = TRANSACTIONFOR[transaction.transactionFor]
        # self.journalTransactionID = transaction.journalTransactionID
        # if transaction.transactionFor == 'personal': # personal transaction
            # assert(type(entity) == Character)
            # entity.transactions.append(self)
        # elif transaction.transactionFor == 'corporation':
            # if type(entity) == Corporation: # we have a corporation api key
                # character = db.session.query(Character).filter(Character.id==transaction.characterID).first()
                # if character is None:
                    # character = Character(transaction.characterID,transaction.characterName)
                    # db.session.add(character)
                    # db.session.flush()
                # character.transactions.append(self)
                # entity.transactions.append(self)

            # else:     # we have a character api key
                # entity.transactions.append(self)
                # self.corpID = entity.corporationID


    # @classmethod
    # def inDB(cls,id):
        # return db.session.query(exists().where(Transaction.id == id)).scalar()


# class Order(db.Model):
    # __tablename__ = 'Order'
    # id = db.Column(db.BigInteger, primary_key=True)
    # volEntered = db.Column(db.Integer)
    # volRemaining = db.Column(db.Integer)
    # minVolume = db.Column(db.Integer)
    # orderState = db.Column(db.Integer) #Valid states: 0 = open/active, 1 = closed, 2 = expired (or fulfilled), 3 = cancelled, 4 = pending, 5 = character deleted.
    # range = db.Column(db.Integer)
    # accountKey = db.Column(db.Integer) # Always 1000 for characters, but in the range 1000 to 1006 for corporations.
    # duration = db.Column(db.Integer)# How many days this order is good for. Expiration is issued + duration in days.
    # escrow = db.Column(db.Float)
    # price = db.Column(db.Float)
    # bid = db.Column(db.Boolean)
    # issued = db.Column(db.DateTime)

    # charID = db.Column(db.Integer, db.ForeignKey('Character.id'))
    # corpID = db.Column(db.Integer, db.ForeignKey('Corporation.id'))

    # typeID = db.Column(db.Integer, db.ForeignKey('invtypes.typeID'))
    # type = db.relationship(InvTypes)

    # stationID = db.Column(db.Integer, db.ForeignKey('stastations.stationID'))
    # station = db.relationship(StaStations)

    # def __init__(self,order,entity):
        # self.id = order.orderID
        # self.stationID = order.stationID
        # self.volEntered = order.volEntered
        # self.volRemaining = order.volRemaining
        # self.minVolume = order.minVolume
        # self.orderState = order.orderState
        # self.typeID = order.typeID
        # self.range = order.range
        # self.accountKey = order.accountKey
        # self.duration = order.duration
        # self.escrow = order.escrow
        # self.price = order.price
        # self.bid = order.bid
        # self.issued = datetime.datetime.fromtimestamp(order.issued)

        # if type(entity) == Corporation: # we have a corporation api key
            # character = db.session.query(Character).filter(Character.id==order.charID).first()
            # if character is None:
                # character = Character(order.charID,None)
                # character.update() # grab name
                # db.session.add(character)
                # db.session.flush()
            # character.orders.append(self)
            # entity.orders.append(self) # corp
        # else:      # we have a character api key
            # assert(entity.id == order.charID) # just to check
            # entity.orders.append(self) # character
            # self.corpID = None

    # def update(self,order,entity):
        # self.volRemaining = order.volRemaining
        # self.orderState = order.orderState
        # self.duration = order.duration
        # self.escrow = order.escrow
        # self.price = order.price
        # self.issued = datetime.datetime.fromtimestamp(order.issued)

    # @classmethod
    # def getByID(cls,id):
        # return db.session.query(Order).filter(Order.id==id).first()

    # @classmethod
    # def getMissingOrders(cls,entity,updated):
        # retVal = []
        # for order in entity.orders:
            # if order.id not in updated:
                # if type(entity)==Character and order.corpID is not None:
                    # # if we have a char api, ignore corp orders
                    # continue
                # else:
                    # retVal.append(order)
        # return retVal

# class Asset(db.Model):
    # __tablename__ = 'Asset'
    # id = db.Column(db.BigInteger, primary_key=True)
    # locationID = db.Column(db.BigInteger)
    # quantity = db.Column(db.Integer)
    # flag = db.Column(db.Integer)
    # singleton = db.Column(db.Boolean)
    # rawQuantity = db.Column(db.Integer)

    # typeID = db.Column(db.Integer, db.ForeignKey('invtypes.typeID'))
    # type = db.relationship(InvTypes)

    # charID = db.Column(db.Integer, db.ForeignKey('Character.id'))
    # corpID = db.Column(db.Integer, db.ForeignKey('Corporation.id'))

    # def __init__(self,asset,entity):
        # self.id = asset.itemID
        # self.typeID = asset.typeID
        # self.quantity = asset.quantity
        # self.flag = asset.flag
        # self.singleton = bool(asset.singleton)
        # try:  # Note that this column is not present in the sub-asset lists
            # self.locationID = asset.locationID
        # except AttributeError, e:
            # self.locationID = None #TODO fix
        # try:
            # self.rawQuantity = asset.rawQuantity
        # except AttributeError, e:
            # self.rawQuantity = None

        # entity.assets.append(self) # will either be corp or char

    # @classmethod
    # def inDB(cls,id):
        # return db.session.query(exists().where(Asset.id == id)).scalar()


# class ItemPrice(db.Model):
    # __tablename__ = 'ItemPrice'
    # transactionType = db.Column(db.Integer,  primary_key=True) # buysell
    # price = db.Column(db.Float)
    # updated = db.Column(db.DateTime)

    # typeID = db.Column(db.Integer, db.ForeignKey('invtypes.typeID'),  primary_key=True)
    # type = db.relationship(InvTypes)

    # solarsystemID = db.Column(db.Integer, db.ForeignKey('mapsolarsystems.solarSystemID'), primary_key=True)
    # solarsystem = db.relationship(MapSolarSystems)

    # def __init__(self,row):
        # self.transactionType = MKTTRANSTYPE[row['buysell']]
        # self.price = row['price']
        # self.updated = row['updated']
        # self.typeID = row['typeID']
        # self.solarsystemID = row['solarsystemID']

    # @classmethod
    # def update(cls,row):
        # price = db.session.query(ItemPrice).filter(ItemPrice.typeID==row['typeID'])\
                                           # .filter(ItemPrice.solarsystemID==row['solarsystemID'])\
                                           # .filter(ItemPrice.transactionType==MKTTRANSTYPE[row['buysell']]).first()
        # if price is None:
            # price = ItemPrice(row)
            # db.session.add(price)
        # else:
            # price.price = row['price']
            # price.updated = row['updated']

# class ItemHistory(db.Model):
    # __tablename__ = 'ItemHistory'
    # typeID = db.Column(db.Integer, db.ForeignKey('invtypes.typeID'),  primary_key=True)
    # type = db.relationship(InvTypes)

    # regionID = db.Column(db.Integer, db.ForeignKey('mapregions.regionID'), primary_key=True)
    # region = db.relationship(MapRegions)

    # date = db.Column(db.DateTime,  primary_key=True)
    # lowPrice = db.Column(db.Float)
    # highPrice = db.Column(db.Float)
    # avgPrice = db.Column(db.Float)
    # volume = db.Column(db.BigInteger)
    # orders = db.Column(db.Integer)

    # def __init__(self,row):
        # self.typeID = row['typeID']
        # self.regionID = row['regionID']
        # self.date = row['date']
        # self.lowPrice = row['lowPrice']
        # self.highPrice = row['highPrice']
        # self.avgPrice = row['avgPrice']
        # self.volume = row['volume']
        # self.orders = row['orders']

    # @classmethod
    # def update(cls,row):
        # history = db.session.query(ItemHistory).filter(ItemHistory.typeID==row['typeID'])\
                                           # .filter(ItemHistory.regionID==row['regionID'])\
                                           # .filter(ItemHistory.date==row['date']).first()
        # if history is None:
            # history = ItemHistory(row)
            # db.session.add(history)
        # else:
            # history.lowPrice = row['lowPrice']
            # history.highPrice = row['highPrice']
            # history.avgPrice = row['avgPrice']
            # history.volume = row['volume']
            # history.orders = row['orders']






