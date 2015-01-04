from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
from flask.ext.login import LoginManager

import settings
import os

app = Flask('wallet',
            template_folder='app/templates',
            static_folder='app/static')
app.config.from_object('app.settings')
app.config.from_envvar('FLASK_SETTINGS')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)

# set up auth
from .users.models import User
login_manager.login_view = "users.login"
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

manager = Manager(app)
manager.add_command('db', MigrateCommand)
#from yamldata import LoadCommand
#manager.add_command('load', LoadCommand)

from .users.views import users
app.register_blueprint(users)

from .api.views import api
app.register_blueprint(api)

import views
import api
