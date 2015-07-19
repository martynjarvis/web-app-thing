import time

from pycrest.eve import APIObject
from pycrest.errors import APIException

from requests.exceptions import ConnectionError

from app import db, celery, eve
from .models import Item, Region, System, Station, MarketHistory, MarketStat
from .tools import get_by_attr_val, get_all_items, item_id_from_crest_href
from app.sso.tools import get_connection

ALPHA = 0.1

COOL_FACTOR = 0.0


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
def update_all_market_history(region_id):
    crest_items = get_all_items(eve.marketTypes)
    for item in crest_items:
        update_market_history.apply_async(args=(region_id, item.type.id))


@celery.task()
def update_all_market_stat(auth_dump, station_id):
    crest_items = get_all_items(eve.marketTypes)
    for item in crest_items:
        update_market_stat.apply_async(args=(auth_dump, station_id,
                                       item.type.id))


@celery.task(rate_limit='30/s')
def update_market_history(region_id, type_id):
    href = "https://public-crest.eveonline.com/market/{0}/types/{1}/history/"

    attempts = 10
    for _ in xrange(attempts):
        try:
            history = APIObject(eve.get(href.format(region_id, type_id)), eve)
            decrease_cool_factor()
            break
        except APIException as ex:
            if "503" in str(ex):
                print "Received 503, we are being rate limited."
                cool_off()
            else:
                raise
        except ConnectionError:
            print "Encountered a ConnectionError."
            cool_off()
    else:
        raise APIException("Continued to receive errors after 10 attempts.")

    if len(history.items) == 0:
        return False

    average_volume = history.items[0].volume
    average_orders = history.items[0].orderCount
    average_price = history.items[0].avgPrice

    # Here I assume results are returned sorted
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
    return True


def percentile(sorted_orders, volume):
    percentile_volume = 5.0*(volume/100)
    running_volume = 0
    for order in sorted_orders:
        running_volume += order.volume
        if running_volume >= percentile_volume:
            return order.price


def get_stats(sorted_orders):
    if len(sorted_orders) > 0:
        current = sorted_orders[0].price
        orders = len(sorted_orders)
        volume = sum(o.volume for o in sorted_orders)
        percent = percentile(sorted_orders, volume)
        return (current, percent, orders, volume)
    else:
        return (None, None, None, None)


@celery.task(rate_limit='15/s')
def update_market_stat(auth_dump, station_id, type_id):
    station_id = int(station_id)
    station = db.session.query(Station).get(station_id)
    region = db.session.query(Region).get(station.region_id)
    item = db.session.query(Item).get(type_id)
    m = MarketStat.get_or_create(station_id=station_id, type_id=type_id)
    con = get_connection(*auth_dump)
    con()  # initialise object
    crest_region = get_by_attr_val(con.regions().items, 'name', region.name)

    attempts = 10
    for _ in xrange(attempts):
        try:
            region_sell_orders = get_all_items(
                crest_region().marketSellOrders(type=item.href))
            region_buy_orders = get_all_items(
                crest_region().marketBuyOrders(type=item.href))
            decrease_cool_factor()
            break
        except APIException as ex:
            if "503" in str(ex):
                print "Received 503, we are being rate limited."
                cool_off()
            else:
                raise
        except ConnectionError:
            print "Encountered a ConnectionError."
            cool_off()
    else:
        raise APIException("Continued to receive errors after 10 attempts.")

    station_sell_orders = sorted(
        (o for o in region_sell_orders if o.location.id == station_id),
        key=lambda o: o.price)
    (m.current_sell, m.current_sell_percentile, m.current_sell_orders,
        m.current_sell_volume) = get_stats(station_sell_orders)

    station_buy_orders = sorted(
        (o for o in region_buy_orders if int(o.location.id) == station_id),
        key=lambda o: o.price, reverse=True)
    (m.current_buy, m.current_buy_percentile, m.current_buy_orders,
        m.current_buy_volume) = get_stats(station_buy_orders)

    db.session.commit()


def cool_off():
    global COOL_FACTOR
    COOL_FACTOR += 2.0
    print "Cooling off for {} seconds before retying.".format(COOL_FACTOR)
    time.sleep(COOL_FACTOR)


def decrease_cool_factor():
    global COOL_FACTOR
    COOL_FACTOR *= 0.95
