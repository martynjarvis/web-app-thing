from flask import session

import base
from evewallet.webapp import auth, db, app

CORP_API_ID = '3548034'
CORP_API_VCODE = 'Js9hbn31hALsFjTCiwoLggwIhzU3RA4cMZFHtMn2lexug1v0vB4t3IHTFCB8SBYE'
CORP_API_CORPORATION_ID = '98280334'
CORP_API_CORPORATION_NAME = 'Large Collidable Object.'

CHAR_API_ID = '3548033'
CHAR_API_VCODE = 'dCzzDgMweF3GUdWQsStk8OiBtsuXY4pGV0Ftdcv4VzGtHFoGsbfbRzRJKznWUezS'
CHAR_API_CHARACTER_ID = '90817766'
CHAR_API_CHARACTER_NAME = 'scruff decima'

class API(base.BaseTest):
    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.rollback()
        db.drop_all()
        
    def test_bad_api(self):
        bad_id = '99999'
        bad_vcode = 'test_wrong_vcode'
        with app.test_client() as c:
            rv = self.create_user(c)
            rv = c.post('/api_add', 
                        data=dict(api_id=bad_id,
                                  api_vcode=bad_vcode), 
                        follow_redirects=True)
                        
            self.assertTrue('API Error' in rv.data)
            
            rv = c.get('/api')
            self.assertFalse(bad_id in rv.data)
            self.assertFalse(bad_vcode in rv.data)
            
        
    def test_char_api(self):
        with app.test_client() as c:
            rv = self.create_user(c)
            rv = c.post('/api_add', 
                        data=dict(api_id=CHAR_API_ID,
                                  api_vcode=CHAR_API_VCODE), 
                        follow_redirects=True)
                        
            self.assertFalse('API Error' in rv.data)
            
            rv = c.get('/api')
            self.assertTrue(CHAR_API_ID in rv.data)
            
            rv = c.get('/characters')
            self.assertTrue(CHAR_API_CHARACTER_NAME in rv.data)
        
    def test_corp_api(self):
        with app.test_client() as c:
            rv = self.create_user(c)
            rv = c.post('/api_add', 
                        data=dict(api_id=CORP_API_ID,
                                  api_vcode=CORP_API_VCODE), 
                        follow_redirects=True)
                        
            self.assertFalse('API Error' in rv.data)
            
            rv = c.get('/api')
            self.assertTrue(CORP_API_ID in rv.data)
        
            rv = c.get('/corporation')
            self.assertTrue(CORP_API_CORPORATION_NAME in rv.data)
 