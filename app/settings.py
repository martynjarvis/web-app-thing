DEBUG=True
SECRET_KEY='dev_key_h8hfne89vm'
CSRF_ENABLED=True
CSRF_SESSION_LKEY='dev_key_h8asSNJ9s9=+'

SQLALCHEMY_DATABASE_URI='sqlite:///data/main.db'
#SQLALCHEMY_DATABASE_URI='mysql+pymysql://test:pleaseignore@localhost/test'

CELERY_BROKER_URL='redis://localhost:6379',
CELERY_RESULT_BACKEND='redis://localhost:6379'
