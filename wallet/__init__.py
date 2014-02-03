from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

import settings

app = Flask('wallet')
app.config.from_object('wallet.settings')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://test.db'
db = SQLAlchemy(app) 
 
import views
import workers
import data