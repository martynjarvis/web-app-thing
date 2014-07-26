from evewallet.webapp import models, db

import yaml

TYPE_ID_FILE = '../data/typeIDs.yaml'
BLUEPRINT_FILE = '../data/blueprints.yaml'

def load_type_id():
    tables = [models.TypeID]
    db.metadata.drop_all(db.engine,tables=[t.__table__ for t in tables])
    db.metadata.create_all(db.engine,tables=[t.__table__ for t in tables])

    type_ids = []
    with open(TYPE_ID_FILE, 'r') as f:
        data = yaml.load(f)
        for k, v in data.iteritems():
            type = models.TypeID(id = k,
                                 graphic_id = v.get('graphicID',None),
                                 radius= v.get('radius',None),
                                 sound_id = v.get('soundID',None),
                                 icon_id = v.get('iconID',None),
                                 faction_id = v.get('factionID',None))
            type_ids.append(type) 
    db.session.add_all(type_ids)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return False
    return True
      
def load_blueprint():
    tables = [models.Blueprint, models.Activity, models.Material, models.Product]
    db.metadata.drop_all(db.engine,tables=[t.__table__ for t in tables])
    db.metadata.create_all(db.engine,tables=[t.__table__ for t in tables])

    blueprints = []
    with open(BLUEPRINT_FILE, 'r') as f:
        data = yaml.load(f)
        for blueprint_id, blueprint in data.iteritems():
            activities = []
            for activity_id, activity in blueprint['activities'].iteritems():
                materials = []
                products = []
                for material_id, material in activity.get('materials',{}).iteritems():
                    materials.append(models.Material(type_id = material_id,
                                                     quantity = material.get('quantity',None),
                                                     consume = material.get('consume',True)))
                for product_id, product in activity.get('products',{}).iteritems():
                    products.append(models.Product(type_id = product_id,
                                                   quantity = product.get('quantity',None),
                                                   probability = product.get('probability',None)))
                
                activities.append(models.Activity(blueprint_id = blueprint_id,
                                                  type = activity_id,
                                                  time = activity.get('time',None),
                                                  materials = materials,
                                                  products = products))

            blueprints.append(models.Blueprint(id = blueprint_id,
                                               production_limit = blueprint.get('maxProductionLimit',None),
                                               activities = activities))
            
    db.session.add_all(blueprints)
    try:
        db.session.commit()  
    except IntegrityError:
        db.session.rollback()
        return False
    return True
    
if __name__ == '__main__':
    load_type_id()
    load_blueprint()