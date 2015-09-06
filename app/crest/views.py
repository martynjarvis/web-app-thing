from flask import Blueprint, redirect, render_template, url_for
from flask.ext.login import login_required

from sqlalchemy.orm import aliased

from pycrest.eve import APIObject

from app import eve, db
from .models import Item, Region, System, Station, MarketHistory, MarketStat
from .forms import SearchForm, ImportForm, UpdateForm, UpdateMarketForm
import tasks
from app.sso.tools import dump_connection, auth_connection


crest = Blueprint('crest', __name__)


@crest.route('/update_items')
@login_required
def update_items():
    tasks.update_items.apply_async()
    return redirect(url_for('index'))


@crest.route('/update_item_prices')
@login_required
def update_item_prices():
    tasks.update_item_prices.apply_async()
    return redirect(url_for('index'))


@crest.route('/update_map')
@login_required
def update_map():
    tasks.update_map.apply_async()
    return redirect(url_for('index'))


@crest.route('/update_history/<int:region_id>')
@login_required
def update_history(region_id):
    tasks.update_market_history.apply_async(args=(region_id, 34))
    return redirect(url_for('index'))


@crest.route('/update_all_history/<int:region_id>')
@login_required
def update_all_history(region_id):
    tasks.update_all_market_history.apply_async(args=(region_id,))
    return redirect(url_for('index'))


@crest.route('/update_stat/<int:region_id>')
@login_required
def update_stat(region_id):
    with auth_connection() as con:
        auth_dump = dump_connection(con)
    tasks.update_market_stat.apply_async(args=(auth_dump, region_id, 34))
    return redirect(url_for('index'))


@crest.route('/update_all_stat/<int:region_id>')
@login_required
def update_all_stat(region_id):
    with auth_connection() as con:
        auth_dump = dump_connection(con)
    tasks.update_all_market_stat.apply_async(args=(auth_dump, region_id))
    return redirect(url_for('index'))


@crest.route('/item/<int:type_id>')
@login_required
def view_item(type_id):
    item = db.session.query(Item).get(type_id)
    crest_item = APIObject(eve.get(item.href), eve)
    market_history = MarketHistory.get_by(type_id=type_id, region_id=10000002)
    market_stat = MarketStat.get_by(type_id=type_id, station_id=60003760)
    return render_template(
        'crest/item_types.html',
        title=item.name,
        item=item,
        crest_item=crest_item(),
        market_history=market_history,
        market_stat=market_stat)


@crest.route('/station/<int:station_id>')
@login_required
def view_station(station_id):
    station = db.session.query(Station).get(station_id)
    return render_template(
        'crest/station.html',
        title=station.name,
        station=station,
        crest_station=None)


@crest.route('/import', methods=['POST', 'GET'])
@login_required
def import_tool():

    form = ImportForm()

    all_stations = db.session.query(Station.facilityID, Station.name)\
        .order_by(Station.name)\
        .all()
    form.destination.choices = (all_stations)

    if form.validate_on_submit():
        dest_market_stat = aliased(MarketStat)
        source_market_stat = aliased(MarketStat)

        dest_market_history = aliased(MarketHistory)
        source_market_history = aliased(MarketHistory)

        dest_station = aliased(Station)
        source_station = aliased(Station)

        dest_region = aliased(Region)
        source_region = aliased(Region)

        data = db.session.query(Item, dest_market_stat, source_market_stat,
                                dest_market_history, source_market_history)\
            .filter(source_region.id == source_station.region_id)\
            .filter(dest_region.id == dest_station.region_id)\
            .filter(source_market_stat.type_id == Item.id)\
            .filter(source_market_stat.station_id == source_station.facilityID)\
            .filter(source_market_stat.current_sell != None)\
            .filter(dest_market_stat.type_id == Item.id)\
            .filter(dest_market_stat.station_id == dest_station.facilityID)\
            .filter(source_market_history.type_id == Item.id)\
            .filter(source_market_history.region_id == source_region.id)\
            .filter(source_market_history.average_price != None)\
            .filter(dest_market_history.average_volume > 0)\
            .filter(dest_market_history.type_id == Item.id)\
            .filter(dest_market_history.region_id == dest_region.id)\
            .filter(dest_market_history.average_price >
                    source_market_stat.current_sell)\
            .filter(source_station.facilityID == form.source.data)\
            .filter(dest_station.facilityID == form.destination.data)\
            .order_by(dest_market_history.price_volume.desc())\
            .all()

    else:
        data = []
    return render_template(
        'crest/import.html',
        title="Import tool",
        data=data,
        form=form,
    )


@crest.route('/search', methods=['POST', 'GET'])
@login_required
def search():
    '''Returns a list of items matching search term'''
    form = SearchForm()
    if form.validate_on_submit():
        data = {}
        data["items"] = db.session.query(Item)\
            .filter(Item.name >= form.search_term.data)\
            .filter(Item.name < form.search_term.data + u"\ufffd")\
            .limit(10)
        data["regions"] = db.session.query(Region)\
            .filter(Region.name >= form.search_term.data)\
            .filter(Region.name < form.search_term.data + u"\ufffd")\
            .limit(10)
        data["systems"] = db.session.query(System)\
            .filter(System.name >= form.search_term.data)\
            .filter(System.name < form.search_term.data + u"\ufffd")\
            .limit(10)
        data["stations"] = db.session.query(Station)\
            .filter(Station.name >= form.search_term.data)\
            .filter(Station.name < form.search_term.data + u"\ufffd")\
            .limit(10)
        return render_template('crest/search.html',
                               title=form.search_term.data,
                               data=data,
                               search_term=form.search_term.data,
                               form=form)
    data = {"items": [], "regions": [], "systems": [], "stations": []}
    return render_template('crest/search.html',
                           title="Search",
                           data=data,
                           search_term="",
                           form=form)


@crest.route('/update_action', methods=['POST'])
@login_required
def update_action():
    update_form = UpdateForm()
    if update_form.validate_on_submit():
        update_tasks = (
            tasks.update_items,
            tasks.update_item_prices,
            tasks.update_map,
        )
        task = update_tasks[update_form.task.data]
        task.apply_async()

    update_market_form = UpdateMarketForm()
    all_regions = db.session.query(Region.id, Region.name)\
        .order_by(Region.name)\
        .all()
    update_market_form.region.choices = (all_regions)

    return render_template(
        'crest/update.html',
        title="Update",
        update_form=update_form,
        update_market_form=update_market_form,
    )


@crest.route('/update_market_action', methods=['POST'])
@login_required
def update_market_action():
    update_market_form = UpdateMarketForm()
    all_regions = db.session.query(Region.id, Region.name)\
        .order_by(Region.name)\
        .all()
    update_market_form.region.choices = (all_regions)

    if update_market_form.validate_on_submit():
        region_id = update_market_form.region.data
        if update_market_form.task.data == 0:
            tasks.update_all_market_history.apply_async(args=(region_id,))
        elif update_market_form.task.data == 1:
            with auth_connection() as con:
                auth_dump = dump_connection(con)
            tasks.update_all_market_stat.apply_async(
                args=(auth_dump, region_id)
            )

    return render_template(
        'crest/update.html',
        title="Update",
        update_form=UpdateForm(),
        update_market_form=update_market_form,
    )


@crest.route('/update', methods=['POST', 'GET'])
@login_required
def update():
    update_market_form = UpdateMarketForm()
    all_regions = db.session.query(Region.id, Region.name)\
        .order_by(Region.name)\
        .all()
    update_market_form.region.choices = (all_regions)

    return render_template(
        'crest/update.html',
        title="Update",
        update_form=UpdateForm(),
        update_market_form=update_market_form,
    )
