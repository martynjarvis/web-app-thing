from flask import session
import mock
import base
from evewallet.webapp import project, db, app

OUTPUT_ID = 12345
OUTPUT_QUANT = 500

class Project(base.BaseTest):
    def setUp(self):
        db.create_all()

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
         
