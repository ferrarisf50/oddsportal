from flask import Flask, render_template, redirect, jsonify, Response
from functions.analysis import RequestObject, analyzation
from flask import session, request, url_for, flash
from werkzeug.datastructures import Headers
from flask.ext.sqlalchemy import SQLAlchemy
from functions.generate_xls import generate_xls

from oddsportal import *

import json, re, datetime, collections, xlwt, StringIO, mimetypes
import models


def labels_getter():

    years, leagues, groups = [], [], []

    ou_values = [0.5, 1, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3, 3.5, 4, 4.5, 5.5]

    leagues = json.loads(open('oddsportal/tmp/leagues.txt').read())
    years   = ['2014', '2013']

    labels  = {'years':     years,
               'leagues':   leagues,
               'ou_values': ou_values}

    return labels


@app.route('/',      methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():

    labels = labels_getter()
    return render_template('index.html', years      = labels.get('years'),
                                         ou_values  = labels.get('ou_values'), 
                                         leagues    = labels.get('leagues'))


@app.route('/download', methods=['GET', 'POST'])
def download():

    raw_results = json.loads(request.values.get('raw_results'))
    table_years = request.values.get('table_years')
    home_teams  = request.values.get('home_teams')
    away_teams  = request.values.get('away_teams')

    response = Response()
    response.status_code = 200

    workbook = generate_xls.generate_xls(raw_results, table_years, home_teams, away_teams)
    output   = StringIO.StringIO()

    workbook.save(output)
    response.data = output.getvalue()

    filename = 'results.xls'
    mimetype_tuple = mimetypes.guess_type(filename)
    response_headers = Headers({
        'Pragma': "public", # required,
        'Cache-Control': 'private', # required for certain browsers,
        'Content-Type': mimetype_tuple[0],
        'Content-Disposition': 'attachment; filename=\"%s\";' % filename,
        'Content-Transfer-Encoding': 'binary',
        'Content-Length': len(response.data)
    })
     
    if not mimetype_tuple[1] is None:
        response.update({
            'Content-Encoding': mimetype_tuple[1]
        })
     
    response.headers = response_headers
    response.set_cookie('fileDownload', 'true', path='/')

    return response


@app.route('/search_results', methods=['GET', 'POST'])
def search_results():

    form_request        = RequestObject(request.form)

    stopwatch_01 = datetime.datetime.now()
    output_results_raw  = analyzation(form_request)
    stopwatch_02 = datetime.datetime.now()
    output_results      = json.loads(output_results_raw)

    time_01 = (stopwatch_02 - stopwatch_01).total_seconds()
    #return jsonify(a=time_01)

    stopwatch_01 = datetime.datetime.now()
    home_teams = []
    for years, teams in output_results['home'].iteritems():
        for team, values in teams['teams'].iteritems():
            home_teams.append(team)
        break
    home_teams = sorted(home_teams)

    away_teams = []
    for years, teams in output_results['away'].iteritems():
        for team, values in teams['teams'].iteritems():
            away_teams.append(team)
        break
    away_teams = sorted(away_teams)

    
    strategies_dict = {'h': 'win at Home', 'a': "win Away", 'd': 'Draw', 'u': 'Under', 'o': 'Over'}
    playing_at_type = 'Home' if form_request.form_playing_at_types == 'h' else 'Away'
    
    if form_request.handicap == 'ou':
        results_labels = {'h': 'Backing at {}-{}'.format(form_request.ou_values, strategies_dict[form_request.strategy]),
                          'a': 'Backing at {}-{}'.format(form_request.ou_values, strategies_dict[form_request.strategy])}
    else:
        results_labels = {'h': 'Backing home teams to {}'.format(strategies_dict[form_request.strategy]),
                          'a': 'Backing away teams to {}'.format(strategies_dict[form_request.strategy])}

    labels = labels_getter()


    for team in home_teams:
        team_all_years_won = 0
        team_all_years_pld = 0
        team_all_years_pl  = 0
        for year in form_request.years:
            team_all_years_won += output_results['home'][year]['teams'][team]['won']
            team_all_years_pld += output_results['home'][year]['teams'][team]['played']
            team_all_years_pl  += output_results['home'][year]['teams'][team]['prft_lss_value']

        for year in form_request.years:
            output_results['home'][year]['teams'][team]['team_all_years_won'] = team_all_years_won
            output_results['home'][year]['teams'][team]['team_all_years_pld'] = team_all_years_pld
            output_results['home'][year]['teams'][team]['team_all_years_pl']  = team_all_years_pl
            break

    for team in away_teams:
        team_all_years_won = 0
        team_all_years_pld = 0
        team_all_years_pl  = 0
        for year in form_request.years:
            team_all_years_won += output_results['away'][year]['teams'][team]['won']
            team_all_years_pld += output_results['away'][year]['teams'][team]['played']
            team_all_years_pl  += output_results['away'][year]['teams'][team]['prft_lss_value']

        for year in form_request.years:
            output_results['away'][year]['teams'][team]['team_all_years_won'] = team_all_years_won
            output_results['away'][year]['teams'][team]['team_all_years_pld'] = team_all_years_pld
            output_results['away'][year]['teams'][team]['team_all_years_pl']  = team_all_years_pl
            break

    
    totals = {'home': {'all_teams_all_years_won': 0,
                       'all_teams_all_years_pld': 0,
                       'all_teams_all_years_pl':  0},
              'away': {'all_teams_all_years_won': 0,
                       'all_teams_all_years_pld': 0,
                       'all_teams_all_years_pl':  0}}


    for year in form_request.years:
        for team in home_teams:
            totals['home']['all_teams_all_years_won'] += output_results['home'][year]['teams'][team]['team_all_years_won']
            totals['home']['all_teams_all_years_pld'] += output_results['home'][year]['teams'][team]['team_all_years_pld']
            totals['home']['all_teams_all_years_pl']  += output_results['home'][year]['teams'][team]['team_all_years_pl']
        break

    for year in form_request.years:
        for team in away_teams:
            totals['away']['all_teams_all_years_won'] += output_results['away'][year]['teams'][team]['team_all_years_won']
            totals['away']['all_teams_all_years_pld'] += output_results['away'][year]['teams'][team]['team_all_years_pld']
            totals['away']['all_teams_all_years_pl']  += output_results['away'][year]['teams'][team]['team_all_years_pl']
        break

    stopwatch_02 = datetime.datetime.now()
    time_02 = (stopwatch_02 - stopwatch_01).total_seconds()
    return render_template("search_results.html", output_results     = output_results,
                                                  table_years        = form_request.years,
                                                  ou_values          = labels.get('ou_values'), 
                                                  leagues            = labels.get('leagues'),
                                                  years              = labels.get('years'),
                                                  home_teams         = home_teams,
                                                  away_teams         = away_teams,
                                                  output_results_raw = output_results_raw,
                                                  results_labels     = results_labels,
                                                  playing_at_type    = form_request.form_playing_at_types,
                                                  group              = form_request.group,
                                                  totals             = totals,
                                                  league             = form_request.league,
                                                  timers             = {'analyse': time_01, 'rest': time_02})



@app.route('/form_checker', methods=['GET', 'POST'])
def form_checker():

    odd_value = request.values.get('odd_value')
    years     = request.values.get('years')

    if not odd_value:
        error = 'Odd value is not selected'
        return jsonify(error = error)

    if not years or years == '':
        error = 'Year(s) not selected'
        return jsonify(error = error)

    return jsonify(error = ' ')


@app.route('/groups_update', methods=['GET', 'POST'])
def groups_update():

    requested_league = request.values.get('lea').strip()

    groups = json.loads(open('oddsportal/tmp/league_groups.txt').read())[requested_league]

    return jsonify(groups = groups)


@app.route('/years_update', methods=['GET', 'POST'])
def years_update():

    requested_group  = request.values.get('grp').strip()
    requested_league = request.values.get('lea').strip()

    years = sorted(json.loads(open('oddsportal/tmp/group_years.txt').read())[requested_league][requested_group])

    return jsonify(years = years)
