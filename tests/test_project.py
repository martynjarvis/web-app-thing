from evewallet.webapp import yamldata, project, db, app

import base
from settings import Blueprint

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
                        data=dict(output_id=Blueprint.product_ids[0],
                                  output_quantity=100), 
                        follow_redirects=True)
            # TODO add a test for projects with n_products > 1

            # check project was made
            self.assertFalse('Project Error' in rv.data)
            rv = c.get('/projects')
            self.assertTrue(str(Blueprint.product_ids[0]) in rv.data)
            projects = project.all_projects()
            self.assertEqual(len(projects), 1)

            # delete project
            rv = c.get('/project_delete/{}'.format(projects[0].id))

            # check project was deleted
            self.assertFalse('Project Error' in rv.data)
            rv = c.get('/project')
            self.assertFalse(str(Blueprint.product_ids[0]) in rv.data)
            projects = project.all_projects()
            self.assertEqual(len(projects), 0)

    def test_bad_delete_project(self):
        with app.test_client() as c:
            rv = self.create_user(c)
            rv = c.get('/project_delete/{}'.format(100),
                       follow_redirects=True)
            self.assertTrue('Project Error' in rv.data)


    def test_project_materials(self):
        with app.test_client() as c:
            rv = self.create_user(c)
            rv = c.post('/project_add',
                        data=dict(output_id=Blueprint.product_ids[0],
                                  output_quantity=Blueprint.n_products),
                        follow_redirects=True)

            projects = project.all_projects()
            self.assertEqual(len(projects), 1)

            raw_materials = [r.type_id for r in projects[0].raw_materials]
            self.assertEqual(len(raw_materials),len(Blueprint.material_ids))
            self.assertEqual(sorted(raw_materials),sorted(Blueprint.material_ids))

            quantities = [r.quantity for r in projects[0].raw_materials]
            self.assertEqual(sorted(quantities),sorted(Blueprint.n_materials))
            
    #def test_t2_project(self):
        #with app.test_client() as c:
            #rv = self.create_user(c)
            ##TODO add to settings.py

            ## add t2 project
            #rv = c.post('/project_add',
                        #data=dict(output_id=OUTPUT_T2_ID,
                                  #output_quantity=OUTPUT_QUANT),
                        #follow_redirects=True)
            #projects = project.all_projects()
            #self.assertEqual(len(projects), 1)
            #project_id = projects[0].id

            # Test data only has:
            #   T2 manafacturing
            #   Invention
            #   T1 manafacturing

            #tasks =  projects[0].tasks
            #self.assertEqual(len(tasks), 3)

            # poor test, need to search by name really
            # rv = c.get('/project_view/{}'.format(project_id))
            # for task in tasks:
                # self.assertTrue(str(task.output_id) in rv.data)



