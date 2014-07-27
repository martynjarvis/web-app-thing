from flask import session
import mock
import base
from evewallet.webapp import yamldata, project, db, app

OUTPUT_ID = base.TYPEID
OUTPUT_T2_ID = 12044  # enyo
OUTPUT_QUANT = 50

from evewallet.webapp import yamldata, db, models

# load test data
yamldata.TYPE_ID_FILE = '../tests/typeIDs_debug.yaml'
yamldata.BLUEPRINT_FILE = '../tests/blueprints_debug.yaml'

class Project(base.BaseTest):
    def setUp(self):
        db.create_all()
        self.load_yaml_data()

    def tearDown(self):
        db.session.rollback()
        db.drop_all()
                    
    def test_add_delete_project(self): 
        with app.test_client() as c:
            rv = self.create_user(c)
            
            # add project
            rv = c.post('/project_add', 
                        data=dict(output_id=OUTPUT_ID,
                                  output_quantity=OUTPUT_QUANT),
                        follow_redirects=True)
                        
            # check project was made
            self.assertFalse('Project Error' in rv.data)                        
            rv = c.get('/project')
            self.assertTrue(str(OUTPUT_ID) in rv.data)
            projects = project.all_projects()
            self.assertEqual(len(projects), 1)
            
            # delete project
            rv = c.get('/project_delete/{}'.format(projects[0].id))
                            
            # check project was deleted
            self.assertFalse('Project Error' in rv.data) 
            rv = c.get('/project')
            self.assertFalse(str(OUTPUT_ID) in rv.data)
            projects = project.all_projects()
            self.assertEqual(len(projects), 0)

    def test_t2_project(self): 
        with app.test_client() as c:
            rv = self.create_user(c)
    
            # add t2 project
            rv = c.post('/project_add', 
                        data=dict(output_id=OUTPUT_T2_ID,
                                  output_quantity=OUTPUT_QUANT),
                        follow_redirects=True)
            projects = project.all_projects()
            self.assertEqual(len(projects), 1)
            project_id = projects[0].id
            
            # Test data only has:
            #   T2 manafacturing
            #   Invention
            #   T1 manafacturing
            
            tasks = project.tasks(project_id)
            self.assertEqual(len(tasks), 3)
            
            rv = c.get('/project_view/{}'.format(project_id))
            for task in tasks:
                self.assertTrue(str(task.output_id) in rv.data)
            

            
    