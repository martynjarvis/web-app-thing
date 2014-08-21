from flask import session

from evewallet.webapp import auth, db, app

import base
from settings import User

class Authentication(base.BaseTest):
    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.rollback()
        db.drop_all()

    def test_bad_login(self):
        with app.test_client() as c:
            rv = self.create_user(c)
            self.assertNotEqual(session.get('user',None),None)

            # log out
            rv = c.get('/logout',follow_redirects=True)
            self.assertEqual(session.get('user',None),None)

            # log in with wrong password
            rv = c.post('/login',
                        data=dict(username=User.username,
                                  password='wrong_password'),
                        follow_redirects=True)

            self.assertTrue('Incorrect username or password' in rv.data)
            self.assertEqual(session.get('user',None), None)

    def test_create_user(self):
        with app.test_client() as c:
            rv = self.create_user(c)
            user_id = session.get('user',None)

            self.assertFalse('Username already in use' in rv.data)
            self.assertFalse('Passwords do not match' in rv.data)

            self.assertNotEqual(user_id, None)
            self.assertEqual(user_id,1)
            self.assertEqual(auth.current_user().username, User.username)
            self.assertEqual(auth.current_user().email, User.email)

    def test_passwords_dont_match(self):
        with app.test_client() as c:
            rv = self.create_user(c, password2='wrong_password')
            user_id = session.get('user',None)

            self.assertFalse('Username already in use' in rv.data)
            self.assertTrue('Passwords do not match' in rv.data)
            self.assertEqual(user_id, None)

    def test_logout_login(self):
        with app.test_client() as c:
            # create a user
            rv = self.create_user(c)
            self.assertNotEqual(session.get('user',None),None)

            # log out
            rv = c.get('/logout',follow_redirects=True)
            self.assertEqual(session.get('user',None),None)

            # log back in
            rv = c.post('/login',
                        data=dict(username=User.username,
                                  password=User.password),
                        follow_redirects=True)
            self.assertNotEqual(session.get('user',None),None)

    def test_create_duplicate_user(self):
        with app.test_client() as c:
            rv = self.create_user(c)
            self.assertNotEqual(session.get('user',None),None)

            # log out
            rv = c.get('/logout',follow_redirects=True)

            # new user
            rv = self.create_user(c, email='new@new',
                                  password1='new', password2='new')

            self.assertEqual(session.get('user',None),None)
            self.assertTrue('Username already in use' in rv.data)
            self.assertFalse('Passwords do not match' in rv.data)
