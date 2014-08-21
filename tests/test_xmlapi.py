from flask import session
import mock

from evewallet.webapp import db, app

import base
from settings import Corp_Api, Char_Api

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
        mock_response = MockResponse(Char_Api.filename, 403)
        instance = mock_HTTPSConnection.return_value
        instance.getresponse.return_value = mock_response

        with app.test_client() as c:
            rv = self.create_user(c)
            rv = c.post('/api_add',
                        data=dict(api_id=Char_Api.key,
                                  api_vcode='AAAAAAA'),
                        follow_redirects=True)

            self.assertTrue('API Error' in rv.data)

            rv = c.get('/api')
            self.assertFalse(Char_Api.key in rv.data)

        mock_response.close()

    @mock.patch("evewallet.eveapi.httplib.HTTPSConnection")
    def test_char_api(self, mock_HTTPSConnection):
        mock_response = MockResponse(Char_Api.filename, 200)
        instance = mock_HTTPSConnection.return_value
        instance.getresponse.return_value = mock_response

        with app.test_client() as c:
            rv = self.create_user(c)
            rv = c.post('/api_add',
                        data=dict(api_id=Char_Api.key,
                                  api_vcode=Char_Api.vcode),
                        follow_redirects=True)

            self.assertFalse('API Error' in rv.data)

            rv = c.get('/api')
            self.assertTrue(Char_Api.key in rv.data)
            self.assertTrue(Char_Api.vcode in rv.data)

            rv = c.get('/characters')
            self.assertTrue(Char_Api.char_name in rv.data)

        mock_response.close()

    @mock.patch("evewallet.eveapi.httplib.HTTPSConnection")
    def test_corp_api(self, mock_HTTPSConnection):
        mock_response = MockResponse(Corp_Api.filename, 200)
        instance = mock_HTTPSConnection.return_value
        instance.getresponse.return_value = mock_response

        with app.test_client() as c:
            rv = self.create_user(c)
            rv = c.post('/api_add',
                        data=dict(api_id=Corp_Api.key,
                                  api_vcode=Corp_Api.vcode),
                        follow_redirects=True)

            self.assertFalse('API Error' in rv.data)

            rv = c.get('/api')
            self.assertTrue(Corp_Api.key in rv.data)
            self.assertTrue(Corp_Api.vcode in rv.data)

            rv = c.get('/corporations')
            self.assertTrue(Corp_Api.corp_name in rv.data)


    @mock.patch("evewallet.eveapi.httplib.HTTPSConnection")
    def test_api_delete(self, mock_HTTPSConnection):
        mock_response = MockResponse(Corp_Api.filename, 200)
        instance = mock_HTTPSConnection.return_value
        instance.getresponse.return_value = mock_response

        with app.test_client() as c:
            rv = self.create_user(c)
            rv = c.post('/api_add',
                        data=dict(api_id=Corp_Api.key,
                                  api_vcode=Corp_Api.vcode),
                        follow_redirects=True)

            self.assertFalse('API Error' in rv.data)

            rv = c.get('/api')
            self.assertTrue(Corp_Api.key in rv.data)
            self.assertTrue(Corp_Api.vcode in rv.data)

            rv = c.get('/api_delete/{}'.format(Corp_Api.key))

            rv = c.get('/api')
            self.assertFalse(Corp_Api.key in rv.data)
            self.assertFalse(Corp_Api.vcode in rv.data)

            # should corps be deleted as well?

    def test_bad_api_delete(self):
        with app.test_client() as c:
            rv = self.create_user(c)
            rv = c.get('/api_delete/{}'.format(100))
            self.assertTrue('API Error' in rv.data)

