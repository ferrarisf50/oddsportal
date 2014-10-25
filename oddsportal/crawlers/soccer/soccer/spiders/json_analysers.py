import re, json


def over_under(response):

    json_response = re.findall(re.compile("dat', (.+?)\);$"), response)[0]
    json_response = json.loads(json_response)

    over_under_full_results = {}

    try:

        #-- Itereating through handicaps --#
        for k,v in json_response['d']['oddsdata']['back'].iteritems():

            label = re.findall(re.compile('-(\d+\.?\d?\d?)-0$'), k)[0]
            #-- Number of odds for handicap type --#
            len_data = len(v['odds'])

            highest_over, highest_under = 0, 0
            total_over,   total_under   = 0, 0
            outer = 0

            try:
                for key, odds in v['odds'].iteritems():
                    #-- Sometimes odds are stored in a dict, somtimes - in a list --#
                    if isinstance(odds, dict):
                        for odd_type, odd in odds.iteritems():
                            #-- Check for the odd not to be False --#
                            if v['act'][key]:
                                if odd_type == '0':
                                    total_under += odd
                                    if odd > highest_under:
                                        highest_under = odd
                                else:
                                    total_over  += odd
                                    if odd > highest_over:
                                        highest_over = odd
                            #-- We want to exclude False odds later so --#
                            #-- we need to know how many of them are --# 
                            else:
                                outer += 0.5

                    else:
                        total_over  += odds[0]
                        total_under += odds[1]
                        if odds[0] > highest_over:
                            highest_over = odds[0]
                        if odds[1] > highest_under:
                            highest_under = odds[1]

            except Exception as e:
                print e
                continue

            if (len_data - outer) == 0:
                over_under_full_results[label] = {'ho': '',
                                                  'hu': '',
                                                  'ao': '',
                                                  'au': ''}
            else:
                average_under = (total_under / (len_data - outer))
                average_over  = (total_over  / (len_data - outer))
                
                over_under_full_results[label] = {'ho': highest_over,
                                                  'hu': highest_under,
                                                  'ao': round(average_over,  3),
                                                  'au': round(average_under, 3)}

        return json.dumps(over_under_full_results)

    except:
        return


def home_draw_away(response):

    json_response = re.findall(re.compile("dat', (.+?)\);$"), response)[0]
    json_response = json.loads(json_response)

    dha_full_results = {}

    try:
        #-- Itereating through handicaps --#
        for k,v in json_response['d']['oddsdata']['back'].iteritems():

            label = re.findall(re.compile('-(\d+\.?\d?\d?)-0$'), k)[0]
            #-- Number of odds for handicap type --#
            len_data = len(v['odds'])

            highest_home, highest_draw, highest_away = 0, 0, 0
            total_home,   total_draw,   total_away   = 0, 0, 0
            outer = 0

            try:
                for key, odds in v['odds'].iteritems():
                    #-- Sometimes odds are stored in a dict, somtimes - in a list --#
                    for odd_type, odd in odds.iteritems():
                        #-- Check for the odd not to be False --#
                        #if v['act'][key]:
                        if odd_type == '0':
                            total_home += odd
                            if odd > highest_home:
                                highest_home = odd
                        elif odd_type == '1':
                            total_draw  += odd
                            if odd > highest_draw:
                                highest_draw = odd
                        elif odd_type == '2':
                            total_away += odd
                            if odd > highest_away:
                                highest_away = odd
                        #-- We want to exclude False odds later so --#
                        #-- we need to know how many of them are --# 
                        #else:
                        #    outer += 0.5

            except Exception as e:
                print e
                continue

            average_home = total_home / len_data
            average_draw = total_draw / len_data
            average_away = total_away / len_data
            
            dha_full_results['hh'] = highest_home
            dha_full_results['hd'] = highest_draw
            dha_full_results['ha'] = highest_away
            dha_full_results['ah'] = round(average_home, 3)
            dha_full_results['ad'] = round(average_draw, 3)
            dha_full_results['aa'] = round(average_away, 3)


        return json.dumps(dha_full_results)

    except Exception as e:
        print e
        print 'ANALYSER Exception'
        print '*'*30
        return