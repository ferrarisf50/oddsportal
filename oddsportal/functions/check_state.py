import socks
import socket
def create_connection(address, timeout=None, source_address=None):
    sock = socks.socksocket()
    sock.connect(address)
    return sock

socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)

# patch the socket module
socket.socket = socks.socksocket
socket.create_connection = create_connection

import urllib2



import sys, os, json, requests

sys.dont_write_bytecode = True
sys.path.append(os.path.abspath(__name__).split('oddsportal')[0] + 'oddsportal/')

import models


results = models.Result.query.filter_by(hda_full_results = None).all()
print len(results)

tournament_url = results[-1].tournament_url
event_hash_01  = results[-1].event_hash_01
event_hash_02  = results[-1].event_hash_02
event_id 	   = results[-1].event_id

event_hash_01  = 'yjcd6'
event_hash_02  = ''
event_id 	   = 'lp15oyx8'

request_link = 'http://fb.oddsportal.com/feed/match/1-1-' + event_id + '-1-2-' + event_hash_01 + '.dat?_=10'
#opener = urllib2.build_opener(urllib2.HTTPHandler)
request_link = str(request_link)

request = urllib2.urlopen(request_link).read()
#request.get_method = lambda: 'PUT'
#url = opener.open(request)
#r = urllib.request.Request('http://www.oddsportal.com')
print request
#print r.status_code
#print [r.text]


#oddsportal.com/soccer/feed/match/1-1-MghwgAl2-5-2-yj22e.dat
#/feed/match/1-1-MghwgAl2-1-2-yj22e.dat