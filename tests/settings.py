# TODO settings should be in caps as thwey're 'global'

class User(object):
    username = 'hello'
    password = 'world'
    email = 'hello@world'

class Blueprint(object):
    type_id = 941
    material_ids = [34,35,36,37,38,39]
    n_materials = [13333,11111,4000,33,17,6]
    product_ids = [594]
    n_products = [1]
    limit = 30
    n_activities = 5

class Yaml_Data(object):
    test_type_id = 34
    type_id_file = './data/typeIDs_debug.yaml'
    blueprint_file = './data/blueprints_debug.yaml'
    
class Corp_Api(object):
    key = '1234567'
    vcode = 'THISISAFAKEAPIVCODE'
    corp_id = '98280334'
    corp_name = 'Large Collidable Object.'
    filename = './data/corp_api_data.txt'

class Char_Api(object):
    key = '1234566'
    vcode = 'THISISANOTHERFAKEAPIVCODE'
    char_id = '90817766'
    char_name = 'scruff decima'
    filename = './data/char_api_data.txt'

#OUTPUT_ID = base.TYPEID # incursus?
#OUTPUT_T2_ID = 12044  # enyo
#OUTPUT_QUANT = 50

# load test data


