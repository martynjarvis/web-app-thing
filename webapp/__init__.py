from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

import settings
import os

tmpl_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'templates'))

app = Flask('wallet', template_folder=tmpl_dir)
app.config.from_object('evewallet.webapp.settings')

db = SQLAlchemy(app) 
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

import models
import views
import workers
import data