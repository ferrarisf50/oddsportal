import sys
sys.dont_write_bytecode = True

from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__)
app.config.from_pyfile('configs/production.py')
#app.config.from_pyfile('configs/development.py')
db = SQLAlchemy(app)

from oddsportal import views
