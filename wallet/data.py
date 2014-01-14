from wallet import app
from models import Item

from google.appengine.ext import ndb

from flask import request,jsonify
    
@app.route('/data/typeahead')
def typeahead_data():
    q = request.args.get('q', 0, type=str)
    data = Item.query().filter(Item.typeName>=q).filter(Item.typeName<q+ u"\ufffd").fetch(4)
    return jsonify(result=[(x.typeID,x.typeName) for x in data])
    
# hack to load eve item data
@app.route('/data/loadevedata')
def load_eve_data():
    with open('./wallet/static/evedata.csv') as f:
        # delete old items
        
        # TODO: ndb.delete_multi(list_of_keys)
        [item.key.delete() for item in Item.query()]
            
        # add new items
        item_list = []
        for line in f:
            line = line.split('\t')
            try :
                marketID = int(line[3])
            except ValueError:
                marketID = None
            item = Item(
                typeID = int(line[0]),
                typeName= str(line[1]),
                volume= float(line[2]),
                marketGroupID = marketID )
            item_list.append(item)
        ndb.put_multi(item_list)
    return 'done'