from pycrest.eve import APIObject
import pycrest

from app import db, celery, eve
from .models import Item, Region, System, Station, MarketHistory, MarketStat
from .tools import get_by_attr_val, get_all_items, item_id_from_crest_href

ALPHA = 0.1


@celery.task()
def update_items():
    updated_items = []
    crest_items = get_all_items(eve.itemTypes)
    for crest_item in crest_items:
        item_id = item_id_from_crest_href(crest_item.href)
        item = Item.get_or_create(id=item_id)
        item.populate_from_object(crest_item)
        updated_items.append(item)

    db.session.commit()

@celery.task()
def update_item_prices():
    updated_items = []
    crest_items = get_all_items(eve.marketPrices)
    for crest_item in crest_items:
        item_id = crest_item.type.id
        item = Item.get_or_create(id=item_id)
        item.populate_from_object(crest_item)
        updated_items.append(item)

    db.session.commit()

@celery.task()
def update_map():
    updated_items = []
    crest_regions = get_all_items(eve.regions)
    for crest_region in crest_regions:
        region_id = item_id_from_crest_href(crest_region.href)
        region = Region.get_or_create(id=region_id)
        region.populate_from_object(crest_region)
        updated_items.append(region)

    crest_systems = get_all_items(eve.industry.systems)
    for crest_system in crest_systems:
        system_id = crest_system.solarSystem.id
        system = System.get_or_create(id=system_id)
        system.populate_from_object(crest_system.solarSystem)
        updated_items.append(system)

    crest_stations = get_all_items(eve.industry.facilities)
    for crest_station in crest_stations:
        station_id = crest_station.facilityID
        station = Station.get_or_create(facilityID=station_id)
        station.populate_from_object(crest_station)
        station.solarSystem_id = crest_station.solarSystem.id
        station.region_id = crest_station.region.id
        station.type_id = crest_station.type.id
        updated_items.append(station)

    db.session.commit()

@celery.task()
def update_market_history(region_id, type_id):
    href = "https://public-crest.eveonline.com/market/{0}/types/{1}/history/"
    history = APIObject(eve.get(href.format(region_id, type_id)), eve)

    # Here I assume results are returned sorted
    average_volume = history.items[0].volume
    average_orders = history.items[0].orderCount
    average_price = history.items[0].avgPrice

    for day in history.items[1:]:
        average_volume = ALPHA*day.volume + average_volume*(1-ALPHA)
        average_orders = ALPHA*day.orderCount + average_orders*(1-ALPHA)
        average_price = ALPHA*day.avgPrice + average_price*(1-ALPHA)

    market_history = MarketHistory.get_or_create(region_id=region_id,
                                                 type_id=type_id)
    market_history.average_volume = average_volume
    market_history.average_orders = average_orders
    market_history.average_price = average_price
    db.session.commit()

@celery.task()
def update_market_stat(auth_con, station_id, type_id):
    station = db.session.query(Station).get(station_id)
    region = db.session.query(Region).get(station.region_id)
    item = db.session.query(Item).get(type_id)
    market_stat = MarketStat.get_or_create(station_id=station_id,
                                           type_id=type_id)

    crest_region = getByAttrVal(auth_con.regions().items, 'name', region.name)

    region_sell_orders = getAllItems(crest_region().marketSellOrders(type=item.href))
    station_sell_orders = sorted(
        (o for o in region_sell_orders if o.location.id==station_id),
        key=lambda o: o.price)
    current_sell = station_sell_orders[0].price
    market_stat.current_sell = current_sell

    region_buy_orders = getAllItems(crest_region().marketBuyOrders(type=item.href))
    station_buy_orders = sorted(
        (o for o in region_buy_orders if o.location.id==station_id),
        key=lambda o: o.price,
        reverse=True)
    current_buy = station_buy_orders[0].price
    market_stat.current_buy = current_buy

    db.session.commit()
