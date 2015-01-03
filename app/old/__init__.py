from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
from flask.ext.login import LoginManager

import settings
import os

tmpl_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'templates'))

app = Flask('wallet', template_folder=tmpl_dir)
app.config.from_object('evewallet.app.settings')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)

# set up auth
from users.models import User
login_manager.login_view = "users.login"
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

from yamldata import LoadCommand

manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command('load', LoadCommand)

#import models
#import views
#import workers
#import data
