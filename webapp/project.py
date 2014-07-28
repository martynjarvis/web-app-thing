from sqlalchemy.exc import IntegrityError

from evewallet.webapp import models, db

def all_projects():
    projects = db.session.query(models.Project).all()
    return projects
    
def get_project(project_id):
    project = db.session.query(models.Project).get(project_id)
    return project

def add_project(output_id, output_quantity): # TODO assert types?
    output_quantity = int(output_quantity)
    project = models.Project(output_id=output_id, output_quantity=output_quantity)
    tasks, raw_materials = create_task(output_id, output_quantity, project.id)
    project.tasks = tasks
    project.raw_materials = raw_materials
    db.session.add(project)
    # try: 
    db.session.commit()
    # except IntegrityError:
        # db.session.rollback()
        # return None    
    return project
    
def create_task(output_id, output_quantity, project_id, parent_task=None, blueprint=False):
    tasks = []
    raw_materials = []
    
    parent_task_id = None
    if parent_task is not None:
        parent_task_id = parent_task.id
        
    # simple implicit join
    q = db.session.query(models.Activity, models.Product).\
                filter(models.Activity.id==models.Product.activity_id).\
                filter(models.Product.type_id==output_id).\
                all()
    if len(q) < 1:
        # A base material or blueprint with no way to make it
        if not blueprint: # don't add T1 blueprints as materials (although with copies maybe this is true...)
            raw_mat = models.RawMaterial(type_id = output_id,
                                        project_id = project_id,
                                        parent_task_id = parent_task_id,
                                        state = 0,
                                        quantity = output_quantity)
            raw_materials.append(raw_mat)
    else:    
        assert(len(q)==1) # Is this guaranteed? I think so...
        
        activity, products = q[0]
        
        current_task = models.Task(output_id=output_id, 
                           output_quantity=output_quantity,
                           project_id=project_id,
                           activity_id=activity.id,
                           parent_task_id = parent_task_id,
                           state = 0)
        tasks.append(current_task)   
        
        # add a task for each product
        for material in activity.materials:
            if material.consume is True:  # ignore decryptors
                new_tasks, new_materials = create_task(material.type_id, output_quantity*material.quantity, project_id, current_task)
                tasks += new_tasks
                raw_materials += new_materials
                
        # add a task for blueprint (invention)
        new_tasks, new_materials = create_task(activity.blueprint_id, output_quantity, project_id, current_task, blueprint=True)
        tasks += new_tasks
        raw_materials += new_materials
        
    return tasks, raw_materials
    
def delete_project(id):
    project = db.session.query(models.Project).get(id)
    if project is None:      
        return None
    db.session.delete(project)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return None
    return True