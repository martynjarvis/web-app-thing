import unittest
from evewallet.webapp import yamldata

TYPEID = 594
BLUEPRINT_ID = 941
BLUEPRINT_MATERIALS = [34,35,36,37,38,39]
BLUEPRINT_MATERIALS_QUANT = [13333,11111,4000,33,17,6]
BLUEPRINT_PRODUCTS = [594]
BLUEPRINT_PRODUCTS_QUANT = [1]
BLUEPRINT_LIMIT = 30
BLUEPRINT_N_ACTV = 5


class BaseTest(unittest.TestCase):
    username = 'hello'
    password = 'world'
    email = 'hello@world'
    
    def load_yaml_data(self):
        yamldata.load_type_id()
        yamldata.load_blueprint()
    
    def create_user(self, context_manager, 
                         username=None,
                         email=None,
                         password1=None,
                         password2=None):
                         
        if username is None:
            username = self.username
        if email is None:
            email = self.email
        if password1 is None:
            password1 = self.password
        if password2 is None:
            password2 = self.password
        
        rv = context_manager.post('/register', 
                                  data=dict(username=username,
                                            email=email,
                                            password1=password1,
                                            password2=password2),
                                  follow_redirects=True)
        return rv    