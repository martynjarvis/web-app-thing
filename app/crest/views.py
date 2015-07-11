import os

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask.ext.login import login_required

from pycrest.eve import APIObject

from app import eve, db
from .tools import get_by_attr_val, get_all_items
from .models import Item, Region, System, Station, MarketHistory, MarketStat
import tasks
from app.sso.views import get_connection

crest = Blueprint('crest', __name__)

@crest.route('/update_items')
def update_items():
    tasks.update_items.apply_async()
    return redirect(url_for('index'))

@crest.route('/update_item_prices')
def update_item_prices():
    tasks.update_item_prices.apply_async()
    return redirect(url_for('index'))

@crest.route('/update_map')
def update_map():
    tasks.update_map.apply_async()
    return redirect(url_for('index'))

@crest.route('/update_history')
def update_history():
    tasks.update_market_history.apply_async(
        args=(10000002, 34))
    return redirect(url_for('index'))

@crest.route('/item/<type_id>')
def view_item(type_id):
    item = db.session.query(Item).get(type_id)
    crest_item = APIObject(eve.get(item.href), eve)
    market_history = MarketHistory.get_by(type_id=type_id, region_id=10000002)
    return render_template(
        'crest/item_types.html',
        title=item.name,
        item=item,
        crest_item=crest_item(),
        market_history=market_history)

@crest.route('/station/<station_id>')
def view_station(station_id):
    station = db.session.query(Station).get(station_id)
    #crest_station = APIObject(eve.get(station.href), eve)
    return render_template(
        'crest/station.html',
        title=station.name,
        station=station,
        crest_station=None)
        #crest_station=crest_station())

@crest.route('/market_type')
def market_types():
    data = get_all_items(eve.marketTypes)
    return render_template('crest/market_types.html',
            title = "Market Types",
            data = data)

@crest.route('/eve', defaults={'path': ""})
@crest.route('/eve/<path:path>')
@login_required
def root(path):
    ''' root crest '''
    data = eve
    name = 'root'
    #try:
    for attr in path.split('/'):
        if attr == "":
            continue
        if isinstance(data,list):
            data = get_by_attr_val(data, 'name', attr)
        else:
            data = getattr(data(), attr)
        name = attr

    if isinstance(data,list):
        return render_template(
            'crest/generic_list.html',
            title = name,
            name = name,
            table_name = name,
            data = data)

    data = data()

    for attr, val in data._dict.iteritems():
        if isinstance(val, list):
            other_data = data
            data = val
            link_fix = os.path.join(name, attr, "")  # Trailing slash

            return render_template(
                'crest/generic_list.html',
                title = name,
                name = name,
                table_name = attr,
                link_fix = link_fix,
                data = data,
                other_data = other_data)

    return render_template(
        'crest/generic.html',
        title = name,
        name = name,
        table_name = name,
        data = data)
