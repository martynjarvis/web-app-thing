import datetime
import eveapi
import os

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
from flask.ext.login import LoginManager

from celery import Celery

import pycrest

import settings

app = Flask('wallet',
            template_folder='app/templates',
            static_folder='app/static')

app.config.from_object('app.settings')
app.config.from_envvar('FLASK_SETTINGS')
app.config.from_envvar('EVE_SSO_SETTINGS')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)

# set up auth
manager = Manager(app)
manager.add_command('db', MigrateCommand)

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
if not os.path.exists(app.config['CREST_CACHE_DIR']):
    os.mkdir(app.config['CREST_CACHE_DIR'])

eve = pycrest.EVE(
    client_id=app.config['CREST_CLIENT_ID'],
    api_key=app.config['CREST_SECRET_KEY'],
    redirect_uri=app.config['CREST_CALLBACK_URL'],
    cache_dir=app.config['CREST_CACHE_DIR'])
eve()  # initialize

from .sso.models import User
login_manager.login_view = "sso.sso_login"
@login_manager.user_loader
def load_user(user_id):
    u = User.query.get(user_id)
    return u

from .sso.views import sso
app.register_blueprint(sso)

from .api.views import api
app.register_blueprint(api)

from .crest.views import crest
app.register_blueprint(crest)

import views
