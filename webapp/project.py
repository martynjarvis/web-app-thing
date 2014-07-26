from flask import session
import hashlib 
from sqlalchemy.exc import IntegrityError

from evewallet.webapp import models, db

def all_projects():
    projects = db.session.query(models.Project).all()
    return projects

def add_project(output_id, output_quantity):
    project = models.Project(output_id=output_id, output_quantity=output_quantity)
    db.session.add(project)
    try: 
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return None    
    return project
    
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