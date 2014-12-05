JSON structure
==============



Templates stored in the database have following structure:
---------------------------------------------------------

{
	'teams_templates': {},
	'calc_templates':  {}
}


'teams_templates' is the one used in 'teams_selecting_box' and has following structure:
--------------------------------------------------------------------------------------

{
	'teams_templates': {'name_of_template': {'home': 'teams;separated;by;colon;',
											 'away': 'teams;separated;by;colon;'}}
}
'selected_teams' is just a string and is always the same


'calc_templates'  is the one used in the right sidebar and has following structure:
----------------------------------------------------------------------------------

{
	'calc_templates': {"ou_values":  '', 
					   "handicap":   '', 
					   "odds_type":  '', 
					   "game_part":  '', 
					   "playing_at": '', 
					   "odd_value":  '', 
					   "years": {"2014": "", 
					   		     "2013-2014": "", 
					   		     "2011-2012": "", 
					   		     "2012-2013": "",
					   		 	 etc}, 
					   "odd_toggle": '', 
					   "strategy":   ''}
}
