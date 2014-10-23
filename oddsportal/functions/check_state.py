import sys, os

sys.dont_write_bytecode = True
sys.path.append(os.path.abspath(__name__).split('oddsportal')[0] + 'oddsportal/')

from flask import session, request, url_for, flash
from oddsportal.functions import json_analysers
import os, json, requests, re, urllib2
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import models



# This script is used to look for empty data in database and
# run crawler again for every missing one

Session = sessionmaker()
engine  = create_engine('postgresql://soccer:soccer@localhost/soccer_db')
Session.configure(bind = engine)
session = Session()
session._model_changes = {}


'''
#-- This is used to enable requests with through Tor   --#
#-- Tor should be installed in order to make this work --#

import socks, socket

def create_connection(address, timeout=None, source_address=None):
    sock = socks.socksocket()
    sock.connect(address)
    return sock

socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
socket.socket = socks.socksocket
socket.create_connection = create_connection
'''

columns_to_check = ['hda_full_results', 
				    'hda_frst_results', 
				    'hda_scnd_results',
				    'ou_full_results',
				    'ou_frst_results',
				    'ou_scnd_results']



def get_results(results, column_to_check):

	for result in results:

		print result.id

		tournament_url = result.tournament_url

		request        = urllib2.urlopen(str(tournament_url)).read()
		event_id       = re.findall(re.compile('"id":"(.+?)"'),    request)[0]
		event_hash_01  = re.findall(re.compile('"xhash":"(.+?)"'), request)[0]

		if column_to_check == 'hda_full_results':
			request_link = 'http://fb.oddsportal.com/feed/match/1-1-{}-1-2-{}.dat?_=100'
		elif column_to_check == 'hda_frst_results':
			request_link = 'http://fb.oddsportal.com/feed/match/1-1-{}-1-3-{}.dat?_=100'
		elif column_to_check == 'hda_scnd_results':
			request_link = 'http://fb.oddsportal.com/feed/match/1-1-{}-1-4-{}.dat?_=100'
		elif column_to_check == 'ou_full_results':
			request_link = 'http://fb.oddsportal.com/feed/match/1-1-{}-2-2-{}.dat?_=100'
		elif column_to_check == 'ou_frst_results':
			request_link = 'http://fb.oddsportal.com/feed/match/1-1-{}-2-3-{}.dat?_=100'
		elif column_to_check == 'ou_scnd_results':
			request_link = 'http://fb.oddsportal.com/feed/match/1-1-{}-2-4-{}.dat?_=100'

		request_link = str(request_link.format(event_id, event_hash_01))

		request  = urllib2.Request(request_link)
		response = urllib2.urlopen(request).read()

		print response

		if 'hda' in column_to_check:
			results  = json_analysers.home_draw_away(response)
		else:
			results  = json_analysers.over_under(response)


		setattr(result, column_to_check, results)
		session.commit()

		print 'Successfully updated row for {}!'.format(column_to_check)


'''
for column_to_check in columns_to_check:

	results = session.query(models.Result).filter(getattr(models.Result, column_to_check) == '{}').all()
	get_results(results, column_to_check)
'''