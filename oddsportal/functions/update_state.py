import sys, os, json

sys.dont_write_bytecode = True
sys.path.append(os.path.abspath(__name__).split('oddsportal')[0] + 'oddsportal/')

import models

try:
    os.remove('../tmp/league_groups.txt')
    os.remove('../tmp/group_years.txt')
    os.remove('../tmp/leagues.txt')
except:
    pass

league_groups_writer = open('../tmp/league_groups.txt', 'w')
group_years_writer   = open('../tmp/group_years.txt',   'w')
leagues_writer       = open('../tmp/leagues.txt',   'w')

leagues = [league[0] for league in set(models.Result.query.with_entities(models.Result.league).all())]

league_groups = {}
group_years   = {}

for league in leagues:
    league_groups[league] = []

    groups = [group[0]  for group in set(
              models.Result.query.filter_by(league = league).with_entities(models.Result.group).all())]

    league_groups[league] = groups
    group_years[league]   = {}

    for group in groups:

        years = [year[0]  for year in set(
                 models.Result.query.filter_by(league = league,
                                               group  = group).with_entities(models.Result.year).all())]

        group_years[league][group] = years



league_groups_writer.write(json.dumps(league_groups))
group_years_writer.write(json.dumps(group_years))
leagues_writer.write(json.dumps(leagues))