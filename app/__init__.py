import datetime
import eveapi
import pycrest
import os

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
from flask.ext.login import LoginManager
from celery import Celery

import settings

app = Flask('wallet',
            template_folder='app/templates',
            static_folder='app/static')
app.config.from_object('app.settings')
try:
    app.config.from_envvar('FLASK_SETTINGS')
except RuntimeError:
    pass  # dev env, set prod env settings in env var

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

# celery stuff
celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
TaskBase = celery.Task
class ContextTask(TaskBase):
    abstract = True
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return TaskBase.__call__(self, *args, **kwargs)
celery.Task = ContextTask

# eveapi stuff
def eveapi_cast_func(key, value):
    # attempts to cast an XML string to the most probable type.
    cast_funcs = (
        lambda x: datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S"),
        int,
        float)

    for f in cast_funcs:
        try:
            return f(value)
        except ValueError:
            pass

    return value  # couldn't cast. return string unchanged.

eveapi.set_cast_func(eveapi_cast_func)
eveapi.set_user_agent("twitter:@_scruff")

# eve crest stuff
eve = pycrest.EVE()
eve()  # initialize

from .users.views import users
app.register_blueprint(users)

from .api.views import api
app.register_blueprint(api)

from .crest.views import crest
app.register_blueprint(crest)

# TODO, are these imports now necessary?
import views
import api
import crest
