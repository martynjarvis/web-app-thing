import time
from flask.ext.login import UserMixin

from pycrest.eve import AuthedConnection

from app import db, eve

class User(UserMixin, db.Model):
    __tablename__ = 'sso_user'
    character_owner_hash = db.Column(db.String(32, convert_unicode=True), primary_key=True)
    character_id = db.Column(db.Integer)
    character_name = db.Column(db.String(50))
    expires = db.Column(db.Integer)  # seconds since epoch for compatibility
    token = db.Column(db.String(50))
    refresh_token = db.Column(db.String(50))

    def __repr__(self):
        return "<User: {}>".format(self.character_name)

    def get_id(self):
        return self.character_owner_hash

    def to_connection(self):
        res = {'access_token': self.token,
               'refresh_token': self.refresh_token,
               'expires_in': 0}
        endpoint = eve._authed_endpoint
        oauth_endpoint = eve._oauth_endpoint
        client_id = eve.client_id
        api_key = eve.api_key
        con = AuthedConnection(
            res,
            endpoint,
            oauth_endpoint,
            client_id,
            api_key,
        )
        if self.expires - int(time.time()) < 20:
            con.refresh()
            self.expires = con.expires
            self.token = con.token
            # self.refresh_token = con.refresh_token 
            # Refresh is actually always the same within the same
            # 'authorisation'
            db.session.commit()
        else:
            con.expires = self.expires

        return con
