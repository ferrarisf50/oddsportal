import sys, os, json, requests, re

sys.dont_write_bytecode = True
sys.path.append(os.path.abspath(__name__).split('oddsportal')[0] + 'oddsportal/')

import models, urllib2

'''
import socks, socket

def create_connection(address, timeout=None, source_address=None):
    sock = socks.socksocket()
    sock.connect(address)
    return sock

socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
socket.socket = socks.socksocket
socket.create_connection = create_connection
'''



results = models.Result.query.filter_by(hda_full_results = '{}').all()
print len(results)


def abc(results):

	tournament_url = results[-3].tournament_url

	request        = urllib2.urlopen(str(tournament_url)).read()
	event_id       = re.findall(re.compile('"id":"(.+?)"'),    request)[0]
	event_hash_01  = re.findall(re.compile('"xhash":"(.+?)"'), request)[0]

	request_link = 'http://fb.oddsportal.com/feed/match/1-1-' + event_id + '-1-2-' + event_hash_01 + '.dat?_=1413966898190'
	request_link = str(request_link)

	request  = urllib2.urlopen(request_link).read()

	url      = request_link
	request  = urllib2.Request(url)

	response = urllib2.urlopen(request)
	print response.read()


abc(results)