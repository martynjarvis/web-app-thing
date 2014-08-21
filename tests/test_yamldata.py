from evewallet.webapp import yamldata, db, models

import base
from settings import Blueprint, Yaml_Data

class YAMLData(base.BaseTest):
    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.rollback()
        db.drop_all()

    def test_load_typeid(self):
        yamldata.load_type_id(filename=Yaml_Data.type_id_file)

        typeID = db.session.query(models.TypeID).get(Yaml_Data.test_type_id)
        self.assertNotEqual(typeID, None)
        self.assertEqual(typeID.id, Yaml_Data.test_type_id)

    def test_load_blueprint(self):
        yamldata.load_blueprint(filename=Yaml_Data.blueprint_file)

        blueprint = db.session.query(models.Blueprint).get(Blueprint.type_id)

        self.assertNotEqual(blueprint, None)
        self.assertEqual(blueprint.production_limit, Blueprint.limit)
        self.assertEqual(len(blueprint.activities), Blueprint.n_activities)

        manafacturing_actv = db.session.query(models.Activity).\
                        filter(models.Activity.blueprint_id==Blueprint.type_id).\
                        filter(models.Activity.type==1).first()

        # TODO sorting?
        self.assertEqual([mat.type_id for mat in manafacturing_actv.materials], Blueprint.material_ids)
        self.assertEqual([mat.quantity for mat in manafacturing_actv.materials], Blueprint.n_materials)

        self.assertEqual([prd.type_id for prd in manafacturing_actv.products], Blueprint.product_ids)
        self.assertEqual([prd.quantity for prd in manafacturing_actv.products], Blueprint.n_products)
