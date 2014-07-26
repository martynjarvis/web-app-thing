from flask import session
import mock
import base
from evewallet.webapp import db, app

CORP_API_ID = '1234567'
CORP_API_VCODE = 'THISISAFAKEAPIVCODE'
CORP_API_CORPORATION_ID = '98280334'
CORP_API_CORPORATION_NAME = 'Large Collidable Object.'
CORP_API_DATA = 'corp_api_data.txt'

CHAR_API_ID = '1234566'
CHAR_API_VCODE = 'THISISAFAKEAPIVCODE'
CHAR_API_CHARACTER_ID = '90817766'
CHAR_API_CHARACTER_NAME = 'scruff decima'
CHAR_API_DATA = 'char_api_data.txt'


class MockResponse(object):
    ''' simple class to mock a HTTP response with data from a file'''
    def __init__(self,xml_file,status=200):
        self.status = status
        self.xml_file = xml_file
        self.file = open(self.xml_file,'r')
    def read(self, nbytes):
        return self.file.read(nbytes)
    def close(self):
        self.file.close()

class API(base.BaseTest):
    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.rollback()
        db.drop_all()

    @mock.patch("evewallet.eveapi.httplib.HTTPSConnection") 
    def test_bad_api(self, mock_HTTPSConnection): 
        mock_response = MockResponse(CHAR_API_DATA, 403)
        instance = mock_HTTPSConnection.return_value
        instance.getresponse.return_value = mock_response
        
        with app.test_client() as c:
            rv = self.create_user(c)
            rv = c.post('/api_add', 
                        data=dict(api_id=CHAR_API_ID,
                                  api_vcode='AAAAAAA'), 
                        follow_redirects=True)
                        
            self.assertTrue('API Error' in rv.data)
            
            rv = c.get('/api')
            self.assertFalse(CHAR_API_ID in rv.data)
            
        mock_response.close()

    @mock.patch("evewallet.eveapi.httplib.HTTPSConnection") 
    def test_char_api(self, mock_HTTPSConnection): 
        mock_response = MockResponse(CHAR_API_DATA, 200)
        instance = mock_HTTPSConnection.return_value
        instance.getresponse.return_value = mock_response

        with app.test_client() as c:
            rv = self.create_user(c)
            rv = c.post('/api_add', 
                        data=dict(api_id=CHAR_API_ID,
                                  api_vcode=CHAR_API_VCODE), 
                        follow_redirects=True)
                        
            self.assertFalse('API Error' in rv.data)
            
            rv = c.get('/api')
            self.assertTrue(CHAR_API_ID in rv.data)
            self.assertTrue(CHAR_API_VCODE in rv.data)
            
            rv = c.get('/characters')
            self.assertTrue(CHAR_API_CHARACTER_NAME in rv.data)
            
        mock_response.close()

    @mock.patch("evewallet.eveapi.httplib.HTTPSConnection") 
    def test_corp_api(self, mock_HTTPSConnection): 
        mock_response = MockResponse(CORP_API_DATA, 200)
        instance = mock_HTTPSConnection.return_value
        instance.getresponse.return_value = mock_response
        
        with app.test_client() as c:
            rv = self.create_user(c)
            rv = c.post('/api_add', 
                        data=dict(api_id=CORP_API_ID,
                                  api_vcode=CORP_API_VCODE), 
                        follow_redirects=True)
                        
            self.assertFalse('API Error' in rv.data)
            
            rv = c.get('/api')
            self.assertTrue(CORP_API_ID in rv.data)
            self.assertTrue(CORP_API_VCODE in rv.data)
        
            rv = c.get('/corporations')
            self.assertTrue(CORP_API_CORPORATION_NAME in rv.data)
            
    # TODO test delete non existant api
    
    @mock.patch("evewallet.eveapi.httplib.HTTPSConnection") 
    def test_api_delete(self, mock_HTTPSConnection): 
        mock_response = MockResponse(CORP_API_DATA, 200)
        instance = mock_HTTPSConnection.return_value
        instance.getresponse.return_value = mock_response
        
        with app.test_client() as c:
            rv = self.create_user(c)
            rv = c.post('/api_add', 
                        data=dict(api_id=CORP_API_ID,
                                  api_vcode=CORP_API_VCODE), 
                        follow_redirects=True)
                        
            self.assertFalse('API Error' in rv.data)
            
            rv = c.get('/api')
            self.assertTrue(CORP_API_ID in rv.data)
            self.assertTrue(CORP_API_VCODE in rv.data)
        
            rv = c.get('/api_delete/{}'.format(CORP_API_ID))
        
            rv = c.get('/api')
            self.assertFalse(CORP_API_ID in rv.data)
            self.assertFalse(CORP_API_VCODE in rv.data)
            
            # should corps be deleted as well?