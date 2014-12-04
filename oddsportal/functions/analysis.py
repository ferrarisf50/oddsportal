import json, collections, re, datetime, os, sys
import models


class RequestObject():

    def __init__(self, request_values):

        [setattr(self, key, value) for key, value in request_values.iteritems()]
        self.years = request_values.getlist('years')
        self.wait_for_win = request_values.getlist('bet_from_win')



def analyzation(form_request):

    path = os.path.dirname(__file__).split('oddsportal')[0]

    def analyze_teams(home_away_teams, results, recent_season_results, playing_at, stake_varying = None):

        def calc(handicap,
                 event_results,
                 strategy,
                 odd,
                 odd_value,
                 ou_value,
                 varying_type,
                 varying_value,
                 varying_stake,
                 number_of_lost_games,
                 number_of_games,
                 waiting_for_win,
                 stop_after):     
            '''Takes event data and returns True of False for Win and Loss and value'''

            def pl_varying_calc(handicap, odd, varying_stake, profit_loss, full_win, half_win):
                if handicap == 'hda':
                    profit_loss_value  = (odd * varying_stake - varying_stake) if profit_loss == 1 else -varying_stake
                elif handicap == 'ou':
                    if   full_win == 1:
                        profit_loss_value =   odd * varying_stake - varying_stake
                    elif half_win == 1:
                        profit_loss_value =  (odd * varying_stake / 2) - varying_stake
                    else:
                        profit_loss_value = -varying_stake
                return profit_loss_value

            def pl_fixed_calc(handicap, odd, odd_value, profit_loss, full_win, half_win):
                if handicap == 'hda':
                    profit_loss_value  = (odd * odd_value - odd_value) if profit_loss == 1 else -odd_value
                elif handicap == 'ou':
                    if   full_win == 1:
                        profit_loss_value =   odd * odd_value - odd_value
                    elif half_win == 1:
                        profit_loss_value =  (odd * odd_value / 2) - odd_value
                    else:
                        profit_loss_value = -odd_value
                return profit_loss_value



            #== PROFIT or LOSS calculation; HALF_WIN of FULL_WIN for Over/Under ==#
            half_win, full_win, profit_loss = 0, 0, 0

            if handicap == 'hda':
                event_home_win = 1 if event_results[0] >  event_results[1] else 0
                event_draw     = 1 if event_results[0] == event_results[1] else 0
                event_away_win = 1 if event_results[0] <  event_results[1] else 0

                if (event_home_win  == 1 and strategy == 'h') or\
                   (event_draw      == 1 and strategy == 'd') or\
                   (event_away_win  == 1 and strategy == 'a'):
                    profit_loss      = 1
            
            elif handicap == 'ou':
                sum_goals = int(event_results[0]) + int(event_results[1])

                if strategy == 'o':
                    if (sum_goals - ou_value)   >= 0.5:
                        full_win, profit_loss    = 1, 1
                    elif (sum_goals - ou_value) >= 0.25:
                        half_win, profit_loss    = 1, 1
                    else:
                        pass

                else:
                    if (ou_value - sum_goals)   >= 0.5:
                        full_win, profit_loss    = 1, 1
                    elif (ou_value - sum_goals) >= 0.25:
                        half_win, profit_loss    = 1, 1
                    else:
                        pass
            #==========================================#

            if waiting_for_win:
                waiting_for_win = False if profit_loss else True
                return [waiting_for_win]

            if stop_after and number_of_lost_games > stop_after:
                waiting_for_win = False if profit_loss else True
                #raise NameError(123)
                return [waiting_for_win]


            #== If "stake varying is enabled " ==#
            if varying_type:

                profit_loss_value = pl_varying_calc(handicap, odd, varying_stake, profit_loss, full_win, half_win)

                if number_of_games and number_of_lost_games > number_of_games:
                    varying_stake = varying_stake
                else:
                    if   varying_type == '1':
                         varying_stake = (varying_stake + varying_stake * varying_value) if not profit_loss else odd_value
                    elif varying_type == '2':
                         varying_stake = (varying_stake + odd_value     * varying_value) if not profit_loss else odd_value

                #-- With every win we reset the number_of_lost_games --#
                number_of_lost_games += 1 if not profit_loss else 0

                if profit_loss:
                    waiting_for_win   = False

                return (profit_loss, round(profit_loss_value, 1), varying_stake, number_of_lost_games, waiting_for_win)

            else:

                profit_loss_value     = pl_fixed_calc(handicap, odd, odd_value, profit_loss, full_win, half_win)
                number_of_lost_games += 1 if not profit_loss else 0

                if profit_loss:
                    waiting_for_win   = False

                return (profit_loss, round(profit_loss_value, 1), varying_stake, number_of_lost_games, waiting_for_win)

            


        output_results = {}
        output_results[playing_at] = {}
        for year in form_request.years:

            if getattr(form_request, year + '_coeff'):
                year_coefficient = re.sub(',', '.', getattr(form_request, year + '_coeff'))
                year_coefficient = float(year_coefficient)
            else:
                year_coefficient = 1

            matches_played_year, matches_won_year, prft_lss_year = 0, 0, 0
            output_results[playing_at][year] = {'r_total_year':  0,
                                                'played_year':   0,
                                                'won_year':      0,
                                                'prft_lss_year': 0,
                                                'coefficient':   year_coefficient,
                                                'teams': {}}

            year_matches = [result for result in results if result.year == year]
            
            for team in home_away_teams:

                #-- Check if team played in the recent season --#
                recent_season_games = [result for result in recent_season_results if result.home_team == team or result.away_team == team]
                recent_season_games = 'active_team' if recent_season_games else 'deactive_team' 

                output_results[playing_at][year]['teams'][team] = {'played':         0,
                                                                   'won':            0,
                                                                   'loss':           0,
                                                                   'prft_lss_value': 0,
                                                                   'r_total':        0,
                                                                   'team_status':    recent_season_games}

                matches_played, matches_won, sum_profit_loss = 0, 0, 0

                where   = 'home_team' if playing_at == 'home' else 'away_team'
                matches = (match for match in year_matches if getattr(match, where) == team)


                #-- Varying_type is which variation option we chose --#
                varying_type  = form_request.varying_type if not form_request.varying_type == '0' else False

                #-- Varying_value is % that we add to varying stake when we lose a game --#
                varying_value = float(form_request.varying_value) / 100 if varying_type and form_request.varying_value else 0

                #-- Varying_stake increases we lose and turns back to odd_value when we win --#
                varying_stake = odd_value

                #-- Number_of_games is the quantity of games the  user set up till the stake varying changes it's behavoir --#
                #-- Number_of_lost_games is increasing every time user loses --#
                number_of_lost_games = 0
                stop_after      = int(form_request.stop_after) if form_request.stop_after else 0
                number_of_games = int(form_request.number_of_games) if varying_type and form_request.number_of_games else 0

                investments = 0
                waiting_for_win = True if '1' in form_request.wait_for_win else False
                
                for match in matches:
                    try:

                        event_results = json.loads(match.event_results)
                        event_results = event_results[form_request.game_part].split(':') if event_results[form_request.game_part] else 0

                        odd = json.loads(getattr(match, results_column))
                        odd = odd[odds_type] if form_request.handicap == 'hda' else odd[str(ou_value)][odds_type]
                        odd = float(odd) - (float(odd) * odd_toggle / 100)

                        handicap, strategy = form_request.handicap, form_request.strategy
                        profit_loss        = calc(handicap,             # 1
                                                  event_results,        # 2
                                                  strategy,             # 3
                                                  odd,                  # 4
                                                  odd_value,            # 5
                                                  ou_value,             # 6
                                                  varying_type,         # 7
                                                  varying_value,        # 8
                                                  varying_stake,        # 9
                                                  number_of_lost_games, # 10
                                                  number_of_games,      # 11
                                                  waiting_for_win,      # 12
                                                  stop_after)           # 13
                        
                        try:
                            varying_stake         = profit_loss[2] if varying_type else odd_value
                            number_of_lost_games  = profit_loss[3]
                            waiting_for_win       = profit_loss[4]
                        except:
                            varying_stake         = varying_stake if varying_type else odd_value
                            if not profit_loss[0]:
                                number_of_lost_games = 0 
                            waiting_for_win       = profit_loss[0]

                        if not waiting_for_win:
                            try:
                                sum_profit_loss  += profit_loss[1] * year_coefficient
                                matches_won      += 1 if profit_loss[0] else 0
                                matches_played   += 1
                                investments      += varying_stake
                            except:
                                pass

                        

                    except Exception as e:
                        continue
                        raise NameError(e)

                matches_played_year += matches_played
                matches_won_year    += matches_won
                prft_lss_year       += sum_profit_loss
                    
                output_results[playing_at][year]['teams'][team]['played']         = matches_played
                output_results[playing_at][year]['teams'][team]['won']            = matches_won
                output_results[playing_at][year]['teams'][team]['loss']           = matches_played - matches_won
                output_results[playing_at][year]['teams'][team]['prft_lss_value'] = sum_profit_loss

                output_results[playing_at][year]['teams'][team]['investments']    = round(investments,1)

            output_results[playing_at][year]['prft_lss_year'] += prft_lss_year
            output_results[playing_at][year]['played_year']    = matches_played_year
            output_results[playing_at][year]['won_year']       = matches_won_year


        return output_results

    timer_01 = datetime.datetime.now()

    

    #-- Check if specific teams were selected instead of League and Group --#
    if form_request.selected_teams_hidden:
        recent_season = '2014' if form_request.summer_winter == 'summer' else '2014-2015'
        #raise NameError(123)
        selected_teams = form_request.selected_teams_hidden.split(';')
        results_01 = models.Result.query.filter(models.Result.home_team.in_(selected_teams),
                                                models.Result.year.in_(form_request.years)).all()
        results_02 = models.Result.query.filter(models.Result.away_team.in_(selected_teams),
                                                models.Result.year.in_(form_request.years)).all()
        results    = results_01 + results_02
        if not results:
            return None

        recent_season_results_01 = models.Result.query.filter(models.Result.home_team.in_(selected_teams),
                                                              models.Result.year   == recent_season).all()
        recent_season_results_02 = models.Result.query.filter(models.Result.away_team.in_(selected_teams),
                                                              models.Result.year   == recent_season).all()
        recent_season_results = recent_season_results_01 + recent_season_results_02

    else:
        #-- Find group's latest season; we later use it to select non-active teams --#
        recent_season = json.loads(open(path + 'oddsportal/oddsportal/tmp/group_years.txt').read())
        recent_season = list(reversed(sorted(recent_season[form_request.league][form_request.group])))[0]

        results = models.Result.query.filter(models.Result.league == form_request.league,
                                             models.Result.group  == form_request.group,
                                             models.Result.year.in_(form_request.years)).all()

        recent_season_results = models.Result.query.filter(models.Result.league == form_request.league,
                                                           models.Result.group  == form_request.group,
                                                           models.Result.year   == recent_season).all()

    results.sort(key=lambda x: x.datetime, reverse=False)

    stopwatch_01 = ((datetime.datetime.now()) - timer_01).total_seconds()

    #leagues = sorted(json.loads(open(path + 'oddsportal/oddsportal/tmp/leagues.txt').read()))
    
   

    timer_01 = datetime.datetime.now()
    if form_request.selected_teams_hidden:
        home_teams = sorted(list(set(selected_teams)))
        away_teams = sorted(list(set(selected_teams)))
    else:
        home_teams = sorted(list(set([result.home_team for result in results])))
        away_teams = sorted(list(set([result.away_team for result in results])))

    results_column = '{}_{}_results'.format(form_request.handicap, form_request.game_part)
    odd_value      = float(form_request.odd_value)
    odd_toggle     = float(form_request.odd_toggle) if form_request.odd_toggle else 0
    odds_type      = form_request.odds_type + form_request.strategy

    try:
        ou_value   = float(form_request.ou_values) if '.' in form_request.ou_values else int(form_request.ou_values)
    except:
        ou_value   = 0

    stopwatch_02 = ((datetime.datetime.now()) - timer_01).total_seconds()

    timer_01 = datetime.datetime.now()
    home_teams_results = analyze_teams(home_teams, results, recent_season_results, 'home')
    away_teams_results = analyze_teams(away_teams, results, recent_season_results, 'away')
    stopwatch_03 = ((datetime.datetime.now()) - timer_01).total_seconds()

    timer_01 = datetime.datetime.now()
    first_value, previous_value = 0, 0


    where = ['home', 'away']
    for w in where:
        where_team_results = eval(w + '_teams_results')
        for k,v in eval(w + '_teams_results')[w].iteritems():
            for i, team in enumerate(eval(w + '_teams')):

                new_value = where_team_results[w][k]['teams'][team]['prft_lss_value']

                if i == 0:
                    where_team_results[w][k]['teams'][team]['r_total'] = new_value
                    previous_value = where_team_results[w][k]['teams'][team]['prft_lss_value']
                else:
                    where_team_results[w][k]['teams'][team]['r_total'] = previous_value + new_value
                    previous_value = where_team_results[w][k]['teams'][team]['r_total']

    

    stopwatch_04 = ((datetime.datetime.now()) - timer_01).total_seconds()
    stopwatches  = [stopwatch_01, stopwatch_02, stopwatch_03, stopwatch_04]



    teams_results = {home_teams_results.keys()[0]: home_teams_results.values()[0],
                     away_teams_results.keys()[0]: away_teams_results.values()[0],
                     'timers': stopwatches}

    return json.dumps(teams_results)