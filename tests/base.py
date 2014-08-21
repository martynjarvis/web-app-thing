import unittest

from evewallet.webapp import yamldata

from settings import User, Yaml_Data

class BaseTest(unittest.TestCase):
    def load_yaml_data(self):
        yamldata.load_type_id(filename=Yaml_Data.type_id_file)
        yamldata.load_blueprint(filename=Yaml_Data.blueprint_file)
    
    def create_user(self, context_manager, 
                         username=None,
                         email=None,
                         password1=None,
                         password2=None):
                         
        if username is None:
            username = User.username
        if email is None:
            email = User.email
        if password1 is None:
            password1 = User.password
        if password2 is None:
            password2 = User.password
        
        rv = context_manager.post('/register', 
                                  data=dict(username=username,
                                            email=email,
                                            password1=password1,
                                            password2=password2),
                                  follow_redirects=True)
        # TODO assert user was created?
        return rv    
