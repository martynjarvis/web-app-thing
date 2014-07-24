import unittest


class BaseTest(unittest.TestCase):
    username = 'hello'
    password = 'world'
    email = 'hello@world'
    
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