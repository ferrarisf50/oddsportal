import sys
sys.dont_write_bytecode = True

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment, Bundle
from hamlish_jinja import HamlishTagExtension
from flask import Flask
from flask.ext import htauth

app = Flask(__name__)

try:
	HTPASSWD = '/tmp/.htpasswd'
	app.config['HTAUTH_HTPASSWD_PATH'] = HTPASSWD
	auth = htauth.HTAuth(app)
except:
	pass


assets = Environment(app)

js_bundle  = Bundle('js/vendor/jquery.min.js',
					'js/custom/dom_ajax.js',
					'js/vendor/foundation.min.js',
					'js/vendor/jquery.sidr.min.js',
					'js/vendor/sweet-alert.min.js',
					'js/vendor/perfect-scrollbar.js', output = 'gen/all.js')

css_bundle = Bundle('css/custom/style.css',
					'css/vendor/font-awesome.css',
					'css/vendor/foundation.css',
					'css/vendor/sidr.dark.css',
					'css/vendor/sweet-alert.css',
					'css/vendor/perfect-scrollbar.css', output = 'gen/all.css')

assets.register('js_all',  js_bundle)
assets.register('css_all', css_bundle)
assets.debug = True
app.config['ASSETS_DEBUG'] = True


app.config.from_pyfile('configs/production.py')
app.jinja_env.add_extension(HamlishTagExtension)
app.jinja_env.hamlish_enable_div_shortcut=True
db = SQLAlchemy(app)


from oddsportal import views