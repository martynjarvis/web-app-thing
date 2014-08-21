import base
from evewallet.webapp import yamldata, db, models

# load test data
yamldata.TYPE_ID_FILE = '../tests/typeIDs_debug.yaml'
yamldata.BLUEPRINT_FILE = '../tests/blueprints_debug.yaml'

class YAMLData(base.BaseTest):
    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.rollback()
        db.drop_all()

    def test_load_typeid(self):
        yamldata.load_type_id()

        typeID = db.session.query(models.TypeID).get(base.TYPEID)
        self.assertNotEqual(typeID, None)
        self.assertEqual(typeID.id, base.TYPEID)

    def test_load_blueprint(self):
        yamldata.load_blueprint()

        blueprint = db.session.query(models.Blueprint).get(base.BLUEPRINT_ID)

        self.assertNotEqual(blueprint, None)
        self.assertEqual(blueprint.production_limit, base.BLUEPRINT_LIMIT)
        self.assertEqual(len(blueprint.activities), base.BLUEPRINT_N_ACTV)

        manafacturing_actv = db.session.query(models.Activity).\
                        filter(models.Activity.blueprint_id==base.BLUEPRINT_ID).\
                        filter(models.Activity.type==1).first()

        self.assertEqual([mat.type_id for mat in manafacturing_actv.materials], base.BLUEPRINT_MATERIALS)
        self.assertEqual([mat.quantity for mat in manafacturing_actv.materials], base.BLUEPRINT_MATERIALS_QUANT)

        self.assertEqual([prd.type_id for prd in manafacturing_actv.products], base.BLUEPRINT_PRODUCTS)
        self.assertEqual([prd.quantity for prd in manafacturing_actv.products], base.BLUEPRINT_PRODUCTS_QUANT)
