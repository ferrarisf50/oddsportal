import xlwt, time, datetime, random, ast



def generate_xls(raw_results, table_years, home_teams, away_teams, totals):

    workbook = xlwt.Workbook()
    raw_results = ast.literal_eval(raw_results)
    table_years = ast.literal_eval(table_years)
    home_teams  = ast.literal_eval(home_teams)
    away_teams  = ast.literal_eval(away_teams)
    totals      = ast.literal_eval(totals)

    style_label = xlwt.XFStyle()
    style_total = xlwt.XFStyle()
    style = xlwt.XFStyle()

    style.alignment.horz = 2

    style_label.alignment.horz = 2
    style_label.font.bold = True


    for where in ['home', 'away']:

        ws = workbook.add_sheet(where)

        ws.write(0, 1, 'Totals', style_label)
        ws.write(1, 1, 'P/L', style_label)
        ws.write(1, 2, '#', style_label)
        ws.write(1, 3, 'W', style_label)

        if where == 'home':
            z = 0
            for a in range(len(home_teams)):
                ws.write(a+2, 1, raw_results['home'][table_years[0]]['teams'][home_teams[a]]['team_all_years_pl'], style)
                ws.write(a+2, 2, raw_results['home'][table_years[0]]['teams'][home_teams[a]]['team_all_years_pld'], style)
                ws.write(a+2, 3, raw_results['home'][table_years[0]]['teams'][home_teams[a]]['team_all_years_won'], style)
                z += 1

            ws.write(z+3, 1, totals['home']['all_teams_all_years_pl'], style_label)
            ws.write(z+3, 2, totals['home']['all_teams_all_years_pld'], style_label)
            ws.write(z+3, 3, totals['home']['all_teams_all_years_won'], style_label)

        else:
            z = 0
            for a in range(len(away_teams)):
                ws.write(a+2, 1, raw_results['away'][table_years[0]]['teams'][away_teams[a]]['team_all_years_pl'], style)
                ws.write(a+2, 2, raw_results['away'][table_years[0]]['teams'][away_teams[a]]['team_all_years_pld'], style)
                ws.write(a+2, 3, raw_results['away'][table_years[0]]['teams'][away_teams[a]]['team_all_years_won'], style)
                z += 1

            ws.write(z+3, 1, totals['away']['all_teams_all_years_pl'], style_label)
            ws.write(z+3, 2, totals['away']['all_teams_all_years_pld'], style_label)
            ws.write(z+3, 3, totals['away']['all_teams_all_years_won'], style_label)


        for i in range(len(table_years)):
            ws.write(0, i*3+5, table_years[i], style_label)
            ws.write(1, i*3+5, 'P/L', style_label)
            ws.write(1, i*3+6, 'Pld/W', style_label)

        if where == 'home':
            for a in range(len(home_teams)):
                ws.write(a+2, 0, home_teams[a])

                e = 5
                for b in range(len(table_years)):
                    ws.write(a+2, e, raw_results[where][table_years[b]]['teams'][home_teams[a]]['prft_lss_value'], style)
                    e+=1
                    win_loss_string = '{}/{}'
                    win_loss_string = win_loss_string.format(raw_results[where][table_years[b]]['teams'][home_teams[a]]['played'], 
                                                             raw_results[where][table_years[b]]['teams'][home_teams[a]]['won'])
                    ws.write(a+2, e, win_loss_string, style)
                    e+=2
        else:
            for a in range(len(away_teams)):
                ws.write(a+2, 0, away_teams[a])

                e = 5
                for b in range(len(table_years)):
                    ws.write(a+2, e, raw_results[where][table_years[b]]['teams'][away_teams[a]]['prft_lss_value'], style)
                    e+=1
                    win_loss_string = '{}/{}'
                    win_loss_string = win_loss_string.format(raw_results[where][table_years[b]]['teams'][away_teams[a]]['played'], 
                                                             raw_results[where][table_years[b]]['teams'][away_teams[a]]['won'])
                    ws.write(a+2, e, win_loss_string, style)
                    e+=2



        if where == 'home':
            e = 5
            for b in range(len(table_years)):
                ws.write(z+3, e,   raw_results['home'][table_years[b]]['prft_lss_year'], style_label)
                ws.write(z+3, e+1, raw_results['home'][table_years[b]]['played_year'], style_label)
                e += 3

        else:
            e = 5
            for b in range(len(table_years)):
                ws.write(z+3, e,   raw_results['away'][table_years[b]]['prft_lss_year'], style_label)
                ws.write(z+3, e+1, raw_results['away'][table_years[b]]['played_year'], style_label)
                e += 3
            
                    
    return workbook