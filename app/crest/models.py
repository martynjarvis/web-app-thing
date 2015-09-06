from sqlalchemy.ext.hybrid import hybrid_property

from app import db
from app.api.models import BaseMixin


class Item(BaseMixin, db.Model):
    __tablename__ = 'crest_item'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    adjustedPrice = db.Column(db.Numeric(12, 2))
    averagePrice = db.Column(db.Numeric(12, 2))
    href = db.Column(db.String(80))
    volume = db.Column(db.Float)
    published = db.Column(db.Boolean)


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
    average_volume = db.Column(db.Float)
    average_orders = db.Column(db.Float)
    average_price = db.Column(db.Numeric(12, 2))

    @hybrid_property
    def price_volume(self):
        return self.average_price * self.average_volume


class MarketStat(BaseMixin, db.Model):
    __tablename__ = 'crest_marketstat'
    type_id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer)  # denormalized
    current_buy = db.Column(db.Numeric(12, 2))
    current_buy_percentile = db.Column(db.Numeric(12, 2))
    current_buy_orders = db.Column(db.Integer)
    current_buy_volume = db.Column(db.Integer)
    current_sell = db.Column(db.Numeric(12, 2))
    current_sell_percentile = db.Column(db.Numeric(12, 2))
    current_sell_orders = db.Column(db.Integer)
    current_sell_volume = db.Column(db.Integer)
