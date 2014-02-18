from webapp import app
# from models import Item

from flask import request,jsonify
    
@app.route('/data/typeahead')
def typeahead_data():
    # q = request.args.get('q', 0, type=str)
    # data = Item.query().filter(Item.typeName>=q).filter(Item.typeName<q+ u"\ufffd").fetch(4)
    # return jsonify(result=[(x.typeID,x.typeName) for x in data])
    return
    