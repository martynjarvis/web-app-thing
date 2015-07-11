from app import db
from app.api.models import BaseMixin

class Item(BaseMixin, db.Model):
    __tablename__ = 'crest_item'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    adjustedPrice = db.Column(db.Numeric(12, 2))
    averagePrice = db.Column(db.Numeric(12, 2))
    href = db.Column(db.String(80))

class Region(BaseMixin, db.Model):
    __tablename__ = 'crest_region'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    href = db.Column(db.String(80))

class System(BaseMixin, db.Model):
    __tablename__ = 'crest_system'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    href = db.Column(db.String(80))
    region_id = db.Column(db.Integer)

class Station(BaseMixin, db.Model):
    __tablename__ = 'crest_station'
    facilityID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    solarSystem_id = db.Column(db.Integer)
    region_id = db.Column(db.Integer)
    type_id = db.Column(db.Integer)

class MarketHistory(BaseMixin, db.Model):
    __tablename__ = 'crest_markethistory'
    type_id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer, primary_key=True)
    average_volume = db.Column(db.Integer)
    average_orders = db.Column(db.Integer)
    average_price = db.Column(db.Numeric(12,2))

class MarketStat(BaseMixin, db.Model):
    __tablename__ = 'crest_marketstat'
    type_id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.Integer, primary_key=True)
    current_buy = db.Column(db.Numeric(12,2))
    current_buy_1day = db.Column(db.Numeric(12,2))
    current_buy_7day = db.Column(db.Numeric(12,2))
    current_sell = db.Column(db.Numeric(12,2))
    current_sell_1day = db.Column(db.Numeric(12,2))
    current_sell_7day = db.Column(db.Numeric(12,2))

