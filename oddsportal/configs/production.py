import os

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = "postgresql://postgres:test123@localhost/postgres"

CSRF_ENABLED = True
SECRET_KEY = 'you shall not pass'
