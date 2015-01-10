from app import db

# LINKS:
#  https://gist.github.com/techniq/5174410
class BaseMixin(object):
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

# could add another mixin that deals with assets and orders, where we have to
# keep track of old orders

ApiCharacter = db.Table('api_apicharacter',
                        db.Column('characterID', db.Integer, db.ForeignKey('api_character.characterID')),
                        db.Column('keyID', db.Integer, db.ForeignKey('api_api.keyID')))

class Api(BaseMixin, db.Model):
    __tablename__ = 'api_api'
    keyID = db.Column(db.Integer, primary_key=True)
    vCode = db.Column(db.String(80))
    accessMask = db.Column(db.Integer)
    expires = db.Column(db.DateTime)
    type = db.Column(db.Enum('Account', 'Character', 'Corporation', name='api_apitypes'))

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

Corporation = None
