import xlwt, time, datetime, random, ast



def generate_xls(raw_results, table_years, home_teams, away_teams):

    workbook = xlwt.Workbook()
    table_years = ast.literal_eval(table_years)
    home_teams  = ast.literal_eval(home_teams)
    away_teams  = ast.literal_eval(away_teams)

    for where in ['home', 'away']:

        ws = workbook.add_sheet(where)

        for i in range(len(table_years)):
            ws.write(0, i*2+1, table_years[i])


        for a in range(len(home_teams)):
            ws.write(a+1, 0, home_teams[a])

            e = 1
            for b in range(len(table_years)):
                ws.write(a+1, e, raw_results[where][table_years[b]]['teams'][home_teams[a]]['prft_lss_value'])
                e+=1
                win_loss_string = '{}/{}'
                win_loss_string = win_loss_string.format(raw_results[where][table_years[b]]['teams'][home_teams[a]]['played'], 
                                                         raw_results[where][table_years[b]]['teams'][home_teams[a]]['won'])
                ws.write(a+1, e, win_loss_string)
                e+=1
                    
    return workbook