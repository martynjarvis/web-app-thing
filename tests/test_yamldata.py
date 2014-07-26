import base
from evewallet.webapp import yamldata, db, models

# load test data
yamldata.TYPE_ID_FILE = '../test/typeIDs_debug.yaml'
yamldata.BLUEPRINT_FILE = '../test/blueprints_debug.yaml'

TYPEID = 38
BLUEPRINT_ID = 681
BLUEPRINT_MATERIALS = [38]
BLUEPRINT_MATERIALS_QUANT = [86]
BLUEPRINT_PRODUCTS = [165]
BLUEPRINT_PRODUCTS_QUANT = [1]
BLUEPRINT_LIMIT = 300
BLUEPRINT_N_ACTV = 4

class YAMLData(base.BaseTest):
    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.rollback()
        db.drop_all()

    def test_load_typeid(self):
        yamldata.load_type_id()
        
        typeID = db.session.query(models.TypeID).get(TYPEID)
        self.assertNotEqual(typeID, None)
        self.assertEqual(typeID.id, TYPEID)
        
    def test_load_blueprint(self):
        yamldata.load_blueprint()
        
        blueprint = db.session.query(models.Blueprint).get(BLUEPRINT_ID)
        
        self.assertNotEqual(blueprint, None)
        self.assertEqual(blueprint.production_limit, BLUEPRINT_LIMIT)
        self.assertEqual(len(blueprint.activities), BLUEPRINT_N_ACTV)
        
        manafacturing_actv = db.session.query(models.Activity).\
                        filter(models.Activity.blueprint_id==BLUEPRINT_ID).\
                        filter(models.Activity.type==1).first()
        
        self.assertEqual([mat.type_id for mat in manafacturing_actv.materials], BLUEPRINT_MATERIALS)
        self.assertEqual([mat.quantity for mat in manafacturing_actv.materials], BLUEPRINT_MATERIALS_QUANT)
        
        self.assertEqual([prd.type_id for prd in manafacturing_actv.products], BLUEPRINT_PRODUCTS)
        self.assertEqual([prd.quantity for prd in manafacturing_actv.products], BLUEPRINT_PRODUCTS_QUANT)