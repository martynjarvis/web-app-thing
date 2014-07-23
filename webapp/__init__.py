from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

import settings

app = Flask('wallet')
app.config.from_object('evewallet.webapp.settings')

db = SQLAlchemy(app) 
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

import models
import views
import workers
import data