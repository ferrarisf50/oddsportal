from flask import Flask, render_template, redirect, jsonify, Response
from functions.analysis import RequestObject, analyzation
from flask import session, request, url_for, flash
from werkzeug.datastructures import Headers
from flask.ext.sqlalchemy import SQLAlchemy
from functions import generate_xls
from flask.ext import htauth

from oddsportal import *
import os

import json, re, datetime, collections, xlwt, StringIO, mimetypes, ast
import models


def labels_getter(session, logged = False):

    if 'login' in session:
        logged = True
        templates = models.User.query.filter_by(login = session['login']).first().templates
        templates = json.loads(templates) if templates else {}
    else:
        templates = {}

    years, leagues, groups = [], [], []
    ou_values = [0.5, 1, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3, 3.5, 4, 4.5, 5.5]

    path    = os.path.dirname(__file__)
    leagues = sorted(json.loads(open(path + '/tmp/leagues.txt').read()))
    years   = ['2014', '2013']

    labels  = {'years':     years,
               'leagues':   leagues,
               'ou_values': ou_values,
               'templates': templates}

    return labels


@app.route('/',      methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@htauth.authenticated
def index(logged = False):


    if 'login' in session:
        logged = True

    labels = labels_getter(session)
    return render_template('index.html', years      = labels.get('years'),
                                         ou_values  = labels.get('ou_values'), 
                                         leagues    = labels.get('leagues'),
                                         templates  = labels.get('templates'),
                                         logged     = logged)


@app.route('/download', methods=['GET', 'POST'])
def download():

    raw_results = request.values.get('output_results')
    table_years = request.values.get('table_years')
    home_teams  = request.values.get('home_teams')
    away_teams  = request.values.get('away_teams')
    totals      = request.values.get('totals')

    response = Response()
    response.status_code = 200

    workbook = generate_xls.generate_xls(raw_results, table_years, home_teams, away_teams, totals)
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
def search_results(logged = False):

    if 'login' in session:
        logged = True

    form_request        = RequestObject(request.form)
    #return jsonify(a = form_request.stake_varying,
    #               b = form_request.varying_value)

    stopwatch_01 = datetime.datetime.now()
    output_results_raw  = analyzation(form_request)
    stopwatch_02 = datetime.datetime.now()
    output_results      = json.loads(output_results_raw)

    time_01 = (stopwatch_02 - stopwatch_01).total_seconds()
    

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

    stake = int(form_request.odd_value)
    
    if form_request.handicap == 'ou':
        results_labels = {'h': 'Backing at {}-{}'.format(form_request.ou_values, strategies_dict[form_request.strategy]),
                          'a': 'Backing at {}-{}'.format(form_request.ou_values, strategies_dict[form_request.strategy])}
    else:
        results_labels = {'h': 'Backing home teams to {}'.format(strategies_dict[form_request.strategy]),
                          'a': 'Backing away teams to {}'.format(strategies_dict[form_request.strategy])}

    labels = labels_getter(session)


    for team in home_teams:
        team_all_years_won = 0
        team_all_years_pld = 0
        team_all_years_pl  = 0
        team_all_years_inv = 0
        for year in form_request.years:
            team_all_years_won += output_results['home'][year]['teams'][team]['won']
            team_all_years_pld += output_results['home'][year]['teams'][team]['played']
            team_all_years_pl  += output_results['home'][year]['teams'][team]['prft_lss_value']
            team_all_years_inv += output_results['home'][year]['teams'][team]['investments']


        for year in form_request.years:
            invest = team_all_years_inv
            roi    = (1 - ((invest - abs(team_all_years_pl)) / invest)) * 100 if team_all_years_won else 100
            roi    = -round(roi, 1) if team_all_years_pl <= 0 else round(roi, 1)
            output_results['home'][year]['teams'][team]['team_all_years_won'] = team_all_years_won
            output_results['home'][year]['teams'][team]['team_all_years_pld'] = team_all_years_pld
            output_results['home'][year]['teams'][team]['team_all_years_pl']  = team_all_years_pl
            output_results['home'][year]['teams'][team]['team_all_years_inv'] = invest
            output_results['home'][year]['teams'][team]['team_all_years_roi'] = roi
            break


    for team in away_teams:
        team_all_years_won = 0
        team_all_years_pld = 0
        team_all_years_pl  = 0
        team_all_years_inv = 0
        for year in form_request.years:
            team_all_years_won += output_results['away'][year]['teams'][team]['won']
            team_all_years_pld += output_results['away'][year]['teams'][team]['played']
            team_all_years_pl  += output_results['away'][year]['teams'][team]['prft_lss_value']
            team_all_years_inv += output_results['home'][year]['teams'][team]['investments']

        for year in form_request.years:
            invest = team_all_years_inv
            roi    = (1 - ((invest - abs(team_all_years_pl)) / invest)) * 100 if invest else 0
            roi    = -round(roi, 1) if team_all_years_pl <= 0 else round(roi, 1)
            output_results['away'][year]['teams'][team]['team_all_years_won'] = team_all_years_won
            output_results['away'][year]['teams'][team]['team_all_years_pld'] = team_all_years_pld
            output_results['away'][year]['teams'][team]['team_all_years_pl']  = team_all_years_pl
            output_results['away'][year]['teams'][team]['team_all_years_inv'] = invest
            output_results['away'][year]['teams'][team]['team_all_years_roi'] = roi
            break

    
    totals = {'home': {'all_teams_all_years_won': 0,
                       'all_teams_all_years_pld': 0,
                       'all_teams_all_years_pl':  0,
                       'all_teams_all_years_inv': 0},
              'away': {'all_teams_all_years_won': 0,
                       'all_teams_all_years_pld': 0,
                       'all_teams_all_years_pl':  0,
                       'all_teams_all_years_inv': 0}}


    for year in form_request.years:
        for team in home_teams:
            totals['home']['all_teams_all_years_won'] += output_results['home'][year]['teams'][team]['team_all_years_won']
            totals['home']['all_teams_all_years_pld'] += output_results['home'][year]['teams'][team]['team_all_years_pld']
            totals['home']['all_teams_all_years_pl']  += output_results['home'][year]['teams'][team]['team_all_years_pl']
            totals['home']['all_teams_all_years_inv'] += output_results['home'][year]['teams'][team]['team_all_years_inv']
        break
    total_investments  = totals['home']['all_teams_all_years_inv']
    total_games_played = totals['home']['all_teams_all_years_pld']
    total_play_loss    = totals['home']['all_teams_all_years_pl']
    totals['home']['all_teams_all_years_roi'] = round(((1 - ((total_investments - abs(total_play_loss)) / total_investments)) * 100), 2)
    totals['home']['all_teams_all_years_roi'] = -totals['home']['all_teams_all_years_roi'] if total_play_loss <= 0 else roi

    for year in form_request.years:
        for team in away_teams:
            totals['away']['all_teams_all_years_won'] += output_results['away'][year]['teams'][team]['team_all_years_won']
            totals['away']['all_teams_all_years_pld'] += output_results['away'][year]['teams'][team]['team_all_years_pld']
            totals['away']['all_teams_all_years_pl']  += output_results['away'][year]['teams'][team]['team_all_years_pl']
            totals['away']['all_teams_all_years_inv'] += output_results['away'][year]['teams'][team]['team_all_years_inv']
        break
    total_investments  = totals['away']['all_teams_all_years_inv']
    total_games_played = totals['away']['all_teams_all_years_pld']
    total_play_loss    = totals['away']['all_teams_all_years_pl']
    totals['away']['all_teams_all_years_roi'] = round(((1 - ((total_investments - abs(total_play_loss)) / total_investments)) * 100), 2) if total_investments else 0
    totals['away']['all_teams_all_years_roi'] = -totals['away']['all_teams_all_years_roi'] if total_play_loss <= 0 else roi

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
                                                  timers             = {'analyse': time_01, 'rest': time_02},
                                                  logged             = logged,
                                                  templates          = labels.get('templates'))



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

    path   = os.path.dirname(__file__)
    groups = json.loads(open(path + '/tmp/league_groups.txt').read())[requested_league]

    return jsonify(groups = groups)


@app.route('/years_update', methods=['GET', 'POST'])
def years_update():

    requested_group  = request.values.get('grp').strip()
    requested_league = request.values.get('lea').strip()

    path  = os.path.dirname(__file__)
    years = sorted(json.loads(open(path + '/tmp/group_years.txt').read())[requested_league][requested_group])

    return jsonify(years = years)


@app.route('/test', methods=['GET', 'POST'])
def test():

    if request.method == 'POST':

        requested_url = request.values.get('url')
        results = models.Result.query.filter_by(tournament_url = requested_url).first()

        if results:
            results = {'home_team':        results.home_team,
                       'away_team':        results.away_team,
                       'league':           results.league,
                       'group':            results.group,
                       'event_results':    results.event_results,
                       'ou_full_results':  results.ou_full_results,
                       'ou_frst_results':  results.ou_frst_results,
                       'ou_scnd_results':  results.ou_scnd_results,
                       'hda_full_results': results.hda_full_results,
                       'hda_frst_results': results.hda_frst_results,
                       'hda_scnd_results': results.hda_scnd_results,
                       'id': results.id}

        error = True if not results else False

        return render_template("test.html", results = results, error = error)


    else:

        return render_template("test.html")




@app.route('/save_template', methods=['GET', 'POST'])
def save_template(logged = False):


    templates = models.User.query.filter_by(login = session['login']).first().templates
    templates = json.loads(templates) if templates else {}

    name = request.values.get('template_name')

    years = json.loads(request.values.get('years'))
    
    template    = {'playing_at':  request.values.get('playing_at'),
                   'handicap':    request.values.get('handicap'),
                   'strategy':    request.values.get('strategy'),
                   'ou_values':   request.values.get('ou_values'),
                   'game_part':   request.values.get('game_part'),
                   'odds_type':   request.values.get('odds_type'),
                   'odd_toggle':  request.values.get('odd_toggle'),
                   'odd_value':   request.values.get('odd_value'),
                   'years':       years}

    templates[name] = json.dumps(template)

    user = models.User.query.filter_by(login = session['login']).first()
    user.templates = json.dumps(templates)

    db.session.add(user)
    db.session.commit()

    return jsonify(templates = templates)




@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = models.User.query.filter_by(login = username).first()
        if user and password == user.password:
            session['login'] = request.form['username']
            return redirect(url_for('index'))
        else:
            error = 'Invalid username or password'
            return jsonify(result = error)

    else:
        return render_template("index.html")

    
@app.route("/registration", methods=['GET', 'POST'])
def registration(error=False):

    if request.method == 'POST':
        
        username = request.form['sign_up_username']
        password = request.form['sign_up_password']
        email    = request.form['sign_up_email']

        login_db = models.User.query.filter_by(login = username).first()
        email_db = models.User.query.filter_by(email = email).first()

        if login_db or email_db:
            error = 'User with the same login or email already exist'
            return render_template("registration.html", error=error)

        user = models.User(login = username, password = password, email = email)
        db.session.add(user)
        db.session.commit()

        return render_template("index.html")
        
        
    else:
        if 'login' in session:
            return render_template("index.html", logged = True)

        return render_template("registration.html", error=error)


@app.route("/logout")
def logout():
    session.pop('login', None)
    return redirect(url_for('index'))



@app.route('/reg_checker', methods=['GET', 'POST'])
def reg_checker():


    username = request.values.get('username')
    email = request.values.get('email')

    login_db = models.User.query.filter_by(login = username).first()
    email_db = models.User.query.filter_by(email = email).first()
    
    username = False if login_db or username == "" else True
    email    = False if email_db or email    == "" else True

    return jsonify(username = username, email = email)




@app.route('/apply_changes', methods=['GET', 'POST'])
def apply_changes():

    game = models.Result.query.filter_by(id = request.values.get('id')).first()

    game.home_team        = request.values.get('home_team')
    game.away_team        = request.values.get('away_team')
    game.league           = request.values.get('league')
    game.group            = request.values.get('group')
    game.event_results    = request.values.get('event_results')
    game.ou_full_results  = request.values.get('ou_full_results')
    game.ou_frst_results  = request.values.get('ou_frst_results')
    game.ou_scnd_results  = request.values.get('ou_scnd_results')
    game.hda_full_results = request.values.get('hda_full_results')
    game.hda_frst_results = request.values.get('hda_frst_results')
    game.hda_scnd_results = request.values.get('hda_scnd_results')

    db.session.add(game)
    db.session.commit()

    return jsonify(message = 'Database updated')
    #http://www.oddsportal.com/soccer/argentina/torneos-de-verano-2008-2009/independiente-racing-club-jTRyAn3Q/



@app.route('/raw_download', methods=['GET', 'POST'])
def raw_download(logged = False):

    if request.method == 'POST':

        league = request.values.get('league')
        group  = request.values.get('group')
        year   = request.values.get('year')

        response = Response()
        response.status_code = 200

        workbook = generate_xls.generate_xls_raw(league, group, year)
        output   = StringIO.StringIO()

        workbook.save(output)
        response.data = output.getvalue()

        filename = 'results_raw.xls'
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



    else:

        if 'login' in session:
            logged = True
            labels = labels_getter(session)

            return render_template('raw_download.html', leagues    = labels.get('leagues'),
                                                        logged     = logged)

        return render_template("index.html")