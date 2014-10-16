import sys
sys.dont_write_bytecode = True

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment, Bundle
from hamlish_jinja import HamlishTagExtension
from flask import Flask

app = Flask(__name__)


assets = Environment(app)
js_bundle  = Bundle('js/website_scripts/all.js',   output = 'gen/all.js')
#css_bundle = Bundle('css/website_scripts/all.css', output = 'gen/all.css')

assets.register('js_all', js_bundle)


app.config.from_pyfile('configs/production.py')
app.jinja_env.add_extension(HamlishTagExtension)
app.jinja_env.hamlish_enable_div_shortcut=True
db = SQLAlchemy(app)


from oddsportal import views