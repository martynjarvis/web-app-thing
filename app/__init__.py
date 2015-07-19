"""
Main script that defines the app
"""
# pylint: disable=relative-import, invalid-name
import datetime
import eveapi
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy  # flask.ext.sqlalchemy
from flask_migrate import Migrate, MigrateCommand  # flask.ext.migrate
from flask_script import Manager  # flask.ext.script
from flask_login import LoginManager  # flask.ext.login
from flask_wtf.csrf import CsrfProtect

from celery import Celery

import pycrest

app = Flask('wallet',
            template_folder='app/templates',
            static_folder='app/static')

# === load configuration
app.config.from_object('app.settings')
app.config.from_envvar('FLASK_SETTINGS')
app.config.from_envvar('EVE_SSO_SETTINGS')

# === initialise app extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

# === celery stuff
celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
TaskBase = celery.Task


class ContextTask(TaskBase):
    """Base class for celery tasks."""
    abstract = True

    def __call__(self, *args, **kwargs):
        with app.app_context():
            return TaskBase.__call__(self, *args, **kwargs)
celery.Task = ContextTask

CsrfProtect(app)


# === eveapi stuff
def eveapi_cast_func(key, value):
    """Attempts to cast an XML string to the most probable type."""
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


# === eve pycrest stuff
if not os.path.exists(app.config['CREST_CACHE_DIR']):
    os.mkdir(app.config['CREST_CACHE_DIR'])

eve = pycrest.EVE(
    client_id=app.config['CREST_CLIENT_ID'],
    api_key=app.config['CREST_SECRET_KEY'],
    redirect_uri=app.config['CREST_CALLBACK_URL'],
    cache_dir=app.config['CREST_CACHE_DIR'])
eve()  # initialize

# === eve login and authentication stuff
from .sso.models import User
login_manager.login_view = "sso.sso_login"


@login_manager.user_loader
def load_user(user_id):
    """Load user object from user's primary key."""
    u = User.query.get(user_id)
    return u

# === imports to initialise views
from .sso.views import sso
app.register_blueprint(sso)

from .api.views import api
app.register_blueprint(api)

from .crest.views import crest
app.register_blueprint(crest)

import views  # noqa
