from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager

import settings
import os

tmpl_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'templates'))

app = Flask('wallet', template_folder=tmpl_dir)
app.config.from_object('evewallet.webapp.settings')

db = SQLAlchemy(app) 
migrate = Migrate(app, db)

from yamldata import LoadCommand

manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command('load', LoadCommand)

import models
import views
import workers
import data