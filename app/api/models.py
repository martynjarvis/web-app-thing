from app import db


class BaseMixin(object):
    """Useful methods to include

    https://gist.github.com/techniq/5174410
    """
    @classmethod
    def get_by(cls, **kw):
        return cls.query.filter_by(**kw).first()

    @classmethod
    def get_or_create(cls, **kw):
        r = cls.get_by(**kw)
        if not r:
            r = cls(**kw)
            db.session.add(r)
        return r

    def populate_from_object(self, obj):
        for n in self.__table__.c.keys():
            if hasattr(obj, n):
                setattr(self, n, getattr(obj, n))

    def __repr__(self):
        values = ', '.join("{0}={1}".format(n, getattr(self, n))
                           for n in self.__table__.c.keys())
        return "{0}({1})".format(self.__class__.__name__, values)

ApiCharacter = db.Table(
    'api_apicharacter',
    db.Column('characterID', db.Integer,
              db.ForeignKey('api_character.characterID')),
    db.Column('keyID', db.Integer, db.ForeignKey('api_api.keyID'))
)

ApiCorporation = db.Table(
    'api_apicorporation',
    db.Column('corporationID', db.Integer,
              db.ForeignKey('api_corporation.corporationID')),
    db.Column('keyID', db.Integer, db.ForeignKey('api_api.keyID'))
)


class Api(BaseMixin, db.Model):
    __tablename__ = 'api_api'
    keyID = db.Column(db.Integer, primary_key=True)
    vCode = db.Column(db.String(80))
    accessMask = db.Column(db.Integer)
    expires = db.Column(db.DateTime)
    type = db.Column(
        db.Enum('Account', 'Character', 'Corporation', name='api_apitypes'))


class Character(BaseMixin, db.Model):
    __tablename__ = 'api_character'
    characterID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    homeStationID = db.Column(db.Integer)
    DoB = db.Column(db.DateTime)
    race = db.Column(db.String(8))
    bloodLine = db.Column(db.String(20))
    ancestry = db.Column(db.String(20))
    gender = db.Column(db.String(6))
    corporationName = db.Column(db.String(80))
    corporationID = db.Column(db.Integer)
    allianceName = db.Column(db.String(80))
    allianceID = db.Column(db.Integer)
    factionName = db.Column(db.String(80))
    factionID = db.Column(db.Integer)
    cloneTypeID = db.Column(db.Integer)
    cloneName = db.Column(db.String(20))
    cloneSkillPoints = db.Column(db.Integer)
    freeSkillPoints = db.Column(db.Integer)
    freeRespecs = db.Column(db.Integer)
    cloneJumpDate = db.Column(db.DateTime)
    lastRespecDate = db.Column(db.DateTime)
    lastTimedRespec = db.Column(db.DateTime)
    remoteStationDate = db.Column(db.DateTime)
    jumpActivation = db.Column(db.DateTime)
    jumpFatigue = db.Column(db.DateTime)
    jumpLastUpdate = db.Column(db.DateTime)
    balance = db.Column(db.Numeric(12, 2))
    apis = db.relationship('Api', secondary=ApiCharacter, backref='characters')


class Corporation(BaseMixin, db.Model):
    __tablename__ = 'api_corporation'
    corporationID = db.Column(db.Integer, primary_key=True)
    corporationName = db.Column(db.String(80))
    ticker = db.Column(db.String(5))
    ceoID = db.Column(db.Integer)
    ceoName = db.Column(db.String(80))
    stationID = db.Column(db.Integer)
    stationName = db.Column(db.String(80))
    description = db.Column(db.String(80))
    url = db.Column(db.String(80))
    allianceID = db.Column(db.Integer)
    factionID = db.Column(db.Integer)
    taxRate = db.Column(db.Float)
    memberCount = db.Column(db.Integer)
    memberLimit = db.Column(db.Integer)
    shares = db.Column(db.Integer)
    apis = db.relationship('Api', secondary=ApiCorporation,
                           backref='corporations')
    # TODO, each api can actually only have a single corporation? is this
    # important?


class Transaction(BaseMixin, db.Model):
    __tablename__ = 'api_transaction'
    transactionDateTime = db.Column(db.DateTime)
    transactionID = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer)
    typeName = db.Column(db.String(80))
    typeID = db.Column(db.Integer)
    price = db.Column(db.Numeric(12, 2))
    clientID = db.Column(db.Integer)
    clientName = db.Column(db.String(80))
    stationID = db.Column(db.Integer)
    stationName = db.Column(db.String(80))
    transactionType = db.Column(
        db.Enum("buy", "sell", name='api_transactiontypes'))
    transactionFor = db.Column(
        db.Enum("personal", "corporation", name='api_transactiontypes'))
    journalTransactionID = db.Column(db.BigInteger)
    clientTypeID = db.Column(db.Integer)

    characterID = db.Column(
        db.Integer, db.ForeignKey('api_character.characterID'), nullable=True)
    character = db.relationship("Character", backref="transactions")

    corporationID = db.Column(
        db.Integer, db.ForeignKey('api_corporation.corporationID'),
        nullable=True)
    corporation = db.relationship("Corporation", backref="transactions")


class Order(BaseMixin, db.Model):
    __tablename__ = 'api_order'
    orderID = db.Column(db.Integer, primary_key=True)
    clientTypeID = db.Column(db.Integer)
    stationID = db.Column(db.Integer)
    volEntered = db.Column(db.Integer)
    volRemaining = db.Column(db.Integer)
    minVolume = db.Column(db.Integer)
    orderState = db.Column(db.Integer)
    typeID = db.Column(db.Integer)
    range = db.Column(db.Integer)
    accountKey = db.Column(db.Integer)
    duration = db.Column(db.Integer)
    escrow = db.Column(db.Numeric(12, 2))
    price = db.Column(db.Numeric(12, 2))
    bid = db.Column(db.Boolean)
    issued = db.Column(db.DateTime)

    # API returns charID :/
    charID = db.Column(
        db.Integer, db.ForeignKey('api_character.characterID'), nullable=True)
    character = db.relationship("Character", backref="orders")

    corporationID = db.Column(
        db.Integer, db.ForeignKey('api_corporation.corporationID'),
        nullable=True)
    corporation = db.relationship("Corporation", backref="orders")
