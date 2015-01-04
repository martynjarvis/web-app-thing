from app import db

class Api(db.Model):
    __tablename__ = 'Api'
    id = db.Column(db.Integer, primary_key=True)
    vcode = db.Column(db.String(80))
    type = db.Column(db.Integer)
    access_mask = db.Column(db.Integer)
    expires = db.Column(db.DateTime)
    type = db.Column(db.Integer)
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

