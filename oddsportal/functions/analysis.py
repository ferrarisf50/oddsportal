import json, collections, re
import models


class RequestObject():

    def __init__(self, request_values):

        [setattr(self, key, value) for key, value in request_values.iteritems()]
        self.years = request_values.getlist('years')



def analyzation(form_request):

    def analyze_teams(home_away_teams, results, playing_at):

        def ou_calc(event_result, strategy, odd, odd_value, ou_value):
            '''Takes event_results and odd, returns True of False for Win and Loss'''

            sum_goals = int(event_result[0]) + int(event_result[1])
            half_win, full_win, profit_loss = 0, 0, 0

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


            if   full_win == 1:
                profit_loss_value =   odd * odd_value
            elif half_win == 1:
                profit_loss_value =  (odd * odd_value / 2) + (odd_value / 2)
            else:
                profit_loss_value = -odd_value

            return (profit_loss, round(profit_loss_value, 1))

        def hda_calc(event_result, strategy, odd, odd_value):
            '''Takes event data and returns True of False for Win and Loss and value'''

            event_home_win = 1 if event_result[0] >  event_result[1] else 0
            event_draw     = 1 if event_result[0] == event_result[1] else 0
            event_away_win = 1 if event_result[0] <  event_result[1] else 0

            profit_loss    = 0
            if (event_home_win  == 1 and strategy == 'h') or\
               (event_draw      == 1 and strategy == 'd') or\
               (event_away_win  == 1 and strategy == 'a'):
                profit_loss      = 1

            profit_loss_value    = (odd*odd_value) if profit_loss == 1 else -odd_value
            return (profit_loss, round(profit_loss_value, 1))


        output_results = {}
        output_results[playing_at] = {}
        for year in form_request.years:

            if getattr(form_request, year+'_coeff'):
                year_coefficient = re.sub(',', '.', getattr(form_request, year+'_coeff'))
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
                output_results[playing_at][year]['teams'][team] = {'played':         0,
                                                                   'won':            0,
                                                                   'loss':           0,
                                                                   'prft_lss_value': 0,
                                                                   'r_total':        0}

                matches_played, matches_won, sum_profit_loss = 0, 0, 0

                ccc = 'home_team' if playing_at == 'home' else 'away_team'
                matches = (match for match in year_matches if getattr(match, ccc) == team)
                
                for match in matches:
                    try:
                        event_results = json.loads(match.event_results)
                        event_results = event_results[form_request.game_part].split(':') if event_results[form_request.game_part] else 0

                        odd = json.loads(getattr(match, results_column))
                        odd = odd[odds_type] if form_request.handicap == 'hda' else odd[str(ou_value)][odds_type]
                        odd = float(odd) - float(odd)*odd_toggle/100

                        profit_loss  = hda_calc(event_results, form_request.strategy, odd, odd_value) if form_request.handicap == 'hda' else\
                                        ou_calc(event_results, form_request.strategy, odd, odd_value, ou_value)
                        
                        sum_profit_loss += profit_loss[1]*year_coefficient
                        matches_won     += 1 if profit_loss[0] else 0
                        matches_played  += 1
                    except Exception as e:
                        continue

                matches_played_year += matches_played
                matches_won_year    += matches_won
                prft_lss_year       += sum_profit_loss
                    
                output_results[playing_at][year]['teams'][team]['played']         = matches_played
                output_results[playing_at][year]['teams'][team]['won']            = matches_won
                output_results[playing_at][year]['teams'][team]['loss']           = matches_played - matches_won
                output_results[playing_at][year]['teams'][team]['prft_lss_value'] = sum_profit_loss

            output_results[playing_at][year]['prft_lss_year'] += prft_lss_year
            output_results[playing_at][year]['played_year']    = matches_played_year
            output_results[playing_at][year]['won_year']       = matches_won_year

        return output_results


    results = models.Result.query.filter(models.Result.league == form_request.league,
                                         models.Result.group  == form_request.group,
                                         models.Result.year.in_(form_request.years)).all()

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

    home_teams_results = analyze_teams(home_teams, results, 'home')
    away_teams_results = analyze_teams(away_teams, results, 'away')


    first_value, previous_value = 0, 0
    for k,v in home_teams_results['home'].iteritems():
        for i, home_team in enumerate(home_teams):

            new_value = home_teams_results['home'][k]['teams'][home_team]['prft_lss_value']

            if i == 0:
                home_teams_results['home'][k]['teams'][home_team]['r_total'] = new_value
                previous_value = home_teams_results['home'][k]['teams'][home_team]['prft_lss_value']
            else:
                home_teams_results['home'][k]['teams'][home_team]['r_total'] = previous_value + new_value
                previous_value = home_teams_results['home'][k]['teams'][home_team]['r_total']


    first_value, previous_value = 0, 0
    for k,v in away_teams_results['away'].iteritems():
        for i, away_team in enumerate(away_teams):

            new_value = away_teams_results['away'][k]['teams'][away_team]['prft_lss_value']

            if i == 0:
                away_teams_results['away'][k]['teams'][away_team]['r_total'] = new_value
                previous_value = away_teams_results['away'][k]['teams'][away_team]['prft_lss_value']
            else:
                away_teams_results['away'][k]['teams'][away_team]['r_total'] = previous_value + new_value
                previous_value = away_teams_results['away'][k]['teams'][away_team]['r_total']



    teams_results = {home_teams_results.keys()[0]: home_teams_results.values()[0],
                     away_teams_results.keys()[0]: away_teams_results.values()[0]}

    return json.dumps(teams_results)