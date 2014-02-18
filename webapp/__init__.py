from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

import settings

app = Flask('wallet')
app.config.from_object('evewallet.webapp.settings')

db = SQLAlchemy(app) 
 
import models
import views
import workers
import data
