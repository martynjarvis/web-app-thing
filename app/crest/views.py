import os

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask.ext.login import login_required

from app import eve

crest = Blueprint('crest', __name__)

def get_by_attr_val(objlist, attr, val):
    ''' Searches list of dicts for a dict with dict[attr] == val '''
    matches = [getattr(obj, attr) == val for obj in objlist]
    index = matches.index(True)  # find first match, raise ValueError if not found
    return objlist[index]

def get_all_items(page):
    ''' Fetch data from all pages '''
    ret = page().items
    while hasattr(page(), 'next'):
        page = page().next()
        ret.extend(page().items)
    return ret

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


# crest api on 25 Apr 2015
#{u'motd': {u'dust': {u'href': u'http://newsfeed.eveonline.com/articles/71'},
#           u'eve': {u'href': u'http://client.eveonline.com/motd/'}, 
#           u'server': {u'href': u'http://client.eveonline.com/motd/'}}, 
#u'crestEndpoint': {u'href': u'https://public-crest.eveonline.com/'}, 
#u'corporationRoles': {u'href': u'https://public-crest.eveonline.com/corporations/roles/'},
#u'itemGroups': {u'href': u'https://public-crest.eveonline.com/inventory/groups/'},
#u'channels': {u'href': u'https://public-crest.eveonline.com/chat/channels/'},
#u'corporations': {u'href': u'https://public-crest.eveonline.com/corporations/'}, 
#u'alliances': {u'href': u'https://public-crest.eveonline.com/alliances/'},
#u'itemTypes': {u'href': u'https://public-crest.eveonline.com/types/'},
#u'decode': {u'href': u'https://public-crest.eveonline.com/decode/'},
#u'battleTheatres': {u'href': u'https://public-crest.eveonline.com/battles/theatres/'},
#u'marketPrices': {u'href': u'https://public-crest.eveonline.com/market/prices/'},
#u'itemCategories': {u'href': u'https://public-crest.eveonline.com/inventory/categories/'},
#u'regions': {u'href': u'https://public-crest.eveonline.com/regions/'},
#u'bloodlines': {u'href': u'https://public-crest.eveonline.com/bloodlines/'},
#u'marketGroups': {u'href': u'https://public-crest.eveonline.com/market/groups/'},
#u'tournaments': {u'href': u'https://public-crest.eveonline.com/tournaments/'}, 
#u'map': {u'href': u'https://public-crest.eveonline.com/map/'},
#u'virtualGoodStore': {u'href': u'https://vgs-tq.eveonline.com/'},
#u'serverVersion': u'EVE-TRANQUILITY 8.53.875004.876723', 
#u'wars': {u'href': u'https://public-crest.eveonline.com/wars/'}, 
#u'incursions': {u'href': u'https://public-crest.eveonline.com/incursions/'}, 
#u'races': {u'href': u'https://public-crest.eveonline.com/races/'},
#u'authEndpoint': {u'href': u'https://login-tq.eveonline.com/oauth/token/'}, 
#u'serviceStatus': {u'dust': u'online', u'eve': u'online', u'server': u'online'},
#u'userCounts': {u'dust': 1790, u'dust_str': u'1790', u'eve': 22382, u'eve_str': u'22382'}, 
#u'industry': {u'facilities': {u'href': u'https://public-crest.eveonline.com/industry/facilities/'},
#              u'systems': {u'href': u'https://public-crest.eveonline.com/industry/systems/'}},
#u'clients': {u'dust': {u'href': u'https://public-crest.eveonline.com/roots/dust/'}, 
#             u'eve': {u'href': u'https://public-crest.eveonline.com/roots/eve/'}},
#u'time': {u'href': u'https://public-crest.eveonline.com/time/'},
#u'marketTypes': {u'href': u'https://public-crest.eveonline.com/market/types/'},
#u'serverName': u'TRANQUILITY'}




