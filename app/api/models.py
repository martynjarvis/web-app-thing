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
        for c in self.__table__.columns:
            setattr(self, c.name, getattr(obj, c.name, default=None))

    def __repr__(self):
        values = ', '.join("{0}={1}".format(n, getattr(self, n))
                           for n in self.__table__.c.keys())
        return "{0}({1})".format(self.__class__.__name__, values)


# could add another mixin that deals with assets and orders, where we have to
# keep track of old orders

class Api(db.Model):
    __tablename__ = 'Api'
    id = db.Column(db.Integer, primary_key=True)
    vcode = db.Column(db.String(80))
    access_mask = db.Column(db.Integer)
    expires = db.Column(db.DateTime)
    type = db.Column(db.Enum('Character', 'Corporation', name='api_types'))

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

