#!/usr/bin/python
import sys
sys.dont_write_bytecode = True

import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/oddsportal/")

from oddsportal import app as application
application.secret_key = 'Add your secret key'
