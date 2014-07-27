from sqlalchemy.exc import IntegrityError

from evewallet.webapp import models, db

def all_projects():
    projects = db.session.query(models.Project).all()
    return projects
    
def tasks(project_id):
    tasks = db.session.query(models.Task).\
                    filter(models.Task.project_id==project_id).\
                    all()
    return tasks

def add_project(output_id, output_quantity):
    project = models.Project(output_id=output_id, output_quantity=output_quantity)
    tasks = create_task(output_id, output_quantity, project.id)
    project.tasks = tasks
    db.session.add(project)
    try: 
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return None    
    return project
    
def create_task(output_id, output_quantity, project_id, parent_task_id=None):
    tasks = []
    # simple implicit join
    q = db.session.query(models.Activity, models.Product).\
                filter(models.Activity.id==models.Product.activity_id).\
                filter(models.Product.type_id==output_id).\
                all()
    if len(q) < 1:
        # A base material or blueprint with no way to make it
        return []
        
    assert(len(q)==1) # Is this guaranteed? I think so...
    
    activity, products = q[0]
    
    task = models.Task(output_id=output_id, 
                          output_quantity=output_quantity,
                          project_id=project_id,
                          activity_id=activity.id,
                          parent_task_id = parent_task_id,
                          state = 0 )    
        
    tasks.append(task)   
    # add a task for each product
    for material in activity.materials:
        tasks += create_task(material.type_id, output_quantity*material.quantity, project_id)
    
    # add a task for blueprint (invention)
    tasks += create_task(activity.blueprint_id, output_quantity, project_id)
    return tasks
    
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