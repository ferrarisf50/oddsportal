import sys, os, json, requests

sys.dont_write_bytecode = True
sys.path.append(os.path.abspath(__name__).split('oddsportal')[0] + 'oddsportal/')

import models


results = models.Result.query.filter_by(hda_full_results = None).all()
print len(results)

for i in results[:100]:
	print i.tournament_url

request_link = 'http://www.oddsportal.com/soccer/feed/match/1-1-vaiVjTk7-1-3-yj68d.dat'
r = requests.get(request_link)
print r.status_code
print [r.text]


