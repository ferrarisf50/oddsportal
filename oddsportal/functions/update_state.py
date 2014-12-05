import sys, os, json
sys.dont_write_bytecode = True
sys.path.append(os.path.abspath(__name__).split('oddsportal')[0] + 'oddsportal/')

import models



def get_leagues_groups():

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


def get_teams():

    summer_winter_teams = {'summer': [], 'winter': []}
    
    for result in models.Result.query.all():
        if '-' in result.year:
            summer_winter_teams['winter'].append(result.home_team + ' -- ' + result.league)
            summer_winter_teams['winter'].append(result.away_team + ' -- ' + result.league)
        else:
            summer_winter_teams['summer'].append(result.home_team + ' -- ' + result.league)
            summer_winter_teams['summer'].append(result.away_team + ' -- ' + result.league)

    summer_winter_teams['winter'] = list(set(summer_winter_teams['winter']))
    summer_winter_teams['summer'] = list(set(summer_winter_teams['summer']))
    teams_writer.write(json.dumps(summer_winter_teams))


def get_teams_years():

    teams = {}
    for result in models.Result.query.all():
        if not teams.get(result.home_team):
            teams[result.home_team] = [result.year]
        else:
            teams[result.home_team].append(result.year)

        if not teams.get(result.away_team):
            teams[result.away_team] = [result.year]
        else:
            teams[result.away_team].append(result.year)

    for name, years in teams.iteritems():
        teams[name] = list(set(teams[name]))

    teams_years_writer.write(json.dumps(teams))

    

def final():

    try:
        os.remove('../tmp/league_groups.txt')
        os.remove('../tmp/group_years.txt')
        os.remove('../tmp/leagues.txt')
        os.remove('../tmp/summer_winter_teams.txt')
        os.remove('../tmp/teams_years.txt')
    except:
        pass

    os.rename('../tmp/league_groups_tmp.txt', '../tmp/league_groups.txt')
    os.rename('../tmp/group_years_tmp.txt', '../tmp/group_years.txt')
    os.rename('../tmp/leagues_tmp.txt', '../tmp/leagues.txt')
    os.rename('../tmp/summer_winter_teams_tmp.txt', '../tmp/summer_winter_teams.txt')
    os.rename('../tmp/teams_years_tmp.txt', '../tmp/teams_years.txt')

    try:
        os.remove('../tmp/league_groups_tmp.txt')
        os.remove('../tmp/group_years_tmp.txt')
        os.remove('../tmp/leagues_tmp.txt')
        os.remove('../tmp/summer_winter_teams_tmp.txt')
        os.remove('../tmp/teams_years_tmp.txt')
    except:
        pass



if __name__ == "__main__":

    league_groups_writer = open('../tmp/league_groups_tmp.txt', 'w')
    group_years_writer   = open('../tmp/group_years_tmp.txt',   'w')
    leagues_writer       = open('../tmp/leagues_tmp.txt',       'w')
    teams_writer         = open('../tmp/summer_winter_teams_tmp.txt', 'w')
    teams_years_writer   = open('../tmp/teams_years_tmp.txt', 'w')

    get_leagues_groups()
    get_teams()
    get_teams_years()
    final()