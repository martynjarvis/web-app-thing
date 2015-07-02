import time

from flask.ext.login import UserMixin

from app import db, eve

class User(UserMixin, db.Model):
    __tablename__ = 'sso_user'
    character_owner_hash = db.Column(db.String(32, convert_unicode=True), primary_key=True)
    character_id = db.Column(db.Integer)
    character_name = db.Column(db.String(50))

    def __repr__(self):
        return "<User: {}>".format(self.character_name)

    def get_id(self):
        return self.character_owner_hash
