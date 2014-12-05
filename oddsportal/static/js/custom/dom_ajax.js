function get_calc_template() {

    var selected_template = $('select[name=select_calc_template]').find(":selected").val();
    var template_values   = JSON.parse(calc_templates[selected_template]);

    for (var x in template_values){
        $('select[name=' + x + ']').val(template_values[x]);
    }

    $('input[name=odd_toggle]').val(template_values['odd_toggle']);
    $('input[name=odd_value]').val(template_values['odd_value']);

    for (var x in template_values['years']) {
        $('input[id=' + x + ']').attr('checked', 'checked');
        $('input[name=' + x + '_coeff]').val(template_values['years'][x]);
    }
    if ($('input[name="odd_value"]').val() === ""){
        $("#error").text("Year or Stake field is empty");
        $('input[type=submit]').attr('disabled', 'disabled');
    }
    else {
        $('input[type=submit]').removeAttr('disabled');
        $("#error").html("")
    };
}


function save_calc_template() {

    var template_name = $('input[name=calc_template_name]').val();


    if (template_name === "") {
        swal("Don't you think tamplate needs a name?");
        return;
    }

    var years_handler = new Object();
    $('input[name = years]:checked').each(function () {
        var year = $(this).val();
        var coeff_label = year + '_coeff'
        var year_coeff = $('input[name=' + coeff_label + ']').val();
        years_handler[year] = year_coeff;
    });

    var years_json = JSON.stringify(years_handler);


    var form_playing_at_types  = $('select[name=form_playing_at_types]').find(":selected").val();
    var handicap    = $('select[name=handicap]').find(":selected").val();
    var strategy    = $('select[name=strategy]').find(":selected").val();
    var ou_values   = $('select[name=ou_values]').find(":selected").val();
    var game_part   = $('select[name=game_part]').find(":selected").val();
    var odds_type   = $('select[name=odds_type]').find(":selected").val();
    var odd_toggle  = $('input[name=odd_toggle]').val();
    var odd_value   = $('input[name=odd_value]').val();

    $.post('/save_calc_template', {

        form_playing_at_types: form_playing_at_types,
        handicap:      handicap,
        strategy:      strategy,
        ou_values:     ou_values,
        game_part:     game_part,
        odds_type:     odds_type,
        odd_toggle:    odd_toggle,
        odd_value:     odd_value,
        template_name: template_name,
        years:         years_json

    }).done(function (data) {
        var templates = data.calc_templates;
        $('select[name=select_calc_template]').empty();

            function templates_appender(selector) {
                $(selector).append('<option disabled selected> -- select a template -- </option>')
                $.each(templates, function (i, v) {
                    $(selector)
                        .append('<option>' + i + '</option>');
                });
            }
            templates_appender('select[name=select_calc_template]');
            swal("Template saved!", "You can now use it.", "success")

    });
}


function delete_calc_template() {
    var selected_template = $('#select_calc_template').find(":selected").val();
    $.post('/delete_calc_template', {
        template_name: selected_template
    }).done(function (data) {
        swal("Template deleted!", "Thank you", "success")
    }); 
}


function save_teams_template() {


    var teams_template_name = $('input[name=teams_template_name]').val();

    if (teams_template_name === "") {
        swal("Don't you think tamplate needs a name?");
        return;
    }

    var selected_teams = $('.selected_teams').text();

    $.post('/save_teams_template', {

        template_name:  teams_template_name,
        selected_teams: selected_teams

    }).done(function (data) {
        var teams_templates = data.teams_templates;
        swal("Template saved!", "You can now use it.", "success")
    });
}


function delete_teams_template() {
    var selected_template = $('#select_teams_template').find(":selected").val();
    $.post('/delete_teams_template', {
        template_name: selected_template
    }).done(function (data) {
        swal("Template deleted!", "Thank you", "success")
    }); 
}



function save_database_changes() {
    
    $.post('/apply_changes', {

        home_team:        $('input[name=home_team]').val(),
        away_team:        $('input[name=away_team]').val(),
        league:           $('input[name=league]').val(),
        group:            $('input[name=group]').val(),
        event_results:    $('input[name=event_results]').val(),
        ou_full_results:  $('input[name=ou_full_results]').val(),
        ou_frst_results:  $('input[name=ou_frst_results]').val(),
        ou_scnd_results:  $('input[name=ou_scnd_results]').val(),
        hda_full_results: $('input[name=hda_full_results]').val(),
        hda_frst_results: $('input[name=hda_frst_results]').val(),
        hda_scnd_results: $('input[name=hda_scnd_results]').val(),
        id : $('input[name=id]').val()

    }).done(function (data) {
        swal("Database updated!", "Thank you for correction.", "success")
    });
}



function signIn() {
    $.post('/login', {
        username: $('input[name="username"]').val(),
        password: $('input[name="password"]').val()

    }).done(function (data) {
        if (data.result) {
            $("#error").text(data.result);
        }
        else {
            window.location.replace("/index");
        };
    });
}



function registration_form_check() {
    $.post('/reg_checker', {

        username: $('input[name="sign_up_username"]').val(),
        email:    $('input[name="sign_up_email"]').val()

    }).done(function (data) {

        if (data.username) {
            $("#username_icon_true").css('display', 'block');
            $("#username_icon_false").css('display', 'none');
        }
        else {
            $("#username_icon_true").css('display', 'none');
            $("#username_icon_false").css('display', 'block');
        };

        if (data.email) {
            $("#email_icon_true").css('display', 'block');
            $("#email_icon_false").css('display', 'none');
        }
        else {
            $("#email_icon_true").css('display', 'none');
            $("#email_icon_false").css('display', 'block');
        };
    });
}


function get_years() {
    var group = $('select[name=group]').find(":selected").text();
    var league = $('select[name=league]').find(":selected").text();
    $('#mySlideContent').html('');

    if (group === '') {
        $('input[name=year]').attr('disabled', 'disabled');
        $('input[name=year_coeff]').attr('disabled', 'disabled');
    }
    else {
        $.post('/years_update', {
            grp: group,
            lea: league
        }).done(function (data) {
            $('#years').html('');
            $('#years_coeffs').html('');

            if (data.years.length > 1) {
                $('#mySlideToggler').show();
            }
            else {
                $('#mySlideToggler').hide();
            }

            var first_year = data.years.slice(-1)
            $('#years').append('<input id="' + first_year + '" name="years" type="checkbox" value="' + first_year +  '"><label>' + first_year + '</label><br>');
            $('#years_coeffs').append('<input id="coefficient" name="' + first_year + '_coeff" type="text" autocomplete="off">');

            for (var i in data.years.slice(1)) {
            
                var year_div    = '<div class="large-7 text-left columns" id="years">'

                var year_input  = '<input id="' + data.years[i] + '" \
                                   name="years" \
                                   type="checkbox" \
                                   value="' + data.years[i] + '">'

                var coeff_div   = '<div class="large-5 columns id="years_coeffs">'

                var coeff_input = '<input id="coefficient" name="' + data.years[i] + '_coeff" type="text" autocomplete="off">'

                $('#mySlideContent').prepend(year_div + year_input + '<label>' + data.years[i] + '</label><br></div>' + coeff_div + coeff_input + '</div>');
            };

            $('#button_save').removeAttr('disabled');
            $('#button_get').removeAttr('disabled');
        }); 
    };
}


function get_groups() {
    var league = $('select[name=league]').find(":selected").text();

    if (league === '') {
        $('select[name=group]').attr('disabled', 'disabled');
    }

    else {
        $.post('/groups_update', {
            lea: league
        }).done(function (data) {
            $('select[name=group]').empty();

            $('select[name=group]').append(new Option(""));
            for (var i in data.groups) {
                $('select[name=group]').append(new Option(data.groups[i], data.groups[i]));
            }
            $('select[name=group]').removeAttr("disabled");
        }); 
    };
}




function search_form_check() {
    var years_selected = [];
    $('#years input:checked').each(function () {
        years_selected.push($(this).attr('value'));
    });
    
    odd_value = $('input[name="odd_value"]').val()
    var selected_teams_hidden = $('.selected_teams_hidden').val();

    if (odd_value && years_selected.length > 0 && selected_teams_hidden) {
        $("#error").text('');
        $('input[type=submit]').removeAttr("disabled");
    }
    else {
        $("#error").text("Year or Stake field is empty");
        $('input[type=submit]').attr('disabled', 'disabled');
    };
}



function handicap_changed_event() {

    var handicap = $("#handicap").find(":selected").text();
    if (handicap == 'H/D/A') {
        $("#ou_values").attr("disabled", "disabled");
        $('#strategy').html('');

        function hda_appender(selector) {

            $(selector)
                .append('<option value="h">Home</option>')
                .append('<option value="d">Draw</option>')
                .append('<option value="a">Away</option>')
        }
        hda_appender('#strategy');

    };

    if (handicap == 'O/U') {
        $("#ou_values").removeAttr("disabled");
        $('#strategy').html('');

        function ou_appender(selector) {

            $(selector)
                .append('<option value="o">Over</option>')
                .append('<option value="u">Under</option>')
        }
        ou_appender('#strategy');

    };
}



function click_result_options(label_away, label_home) {
    
    if ($('.result_options').text() === 'Switch to away teams') {
        $('#results_label').html(label_away);
        $('.result_options').html('Switch to <span class="higlighted">home</span> teams');
    }
    else {
        $('#results_label').html(label_home);
        $('.result_options').html('Switch to <span class="higlighted">away</span> teams');
    };

    if ($('#home_results_table').is(":visible")) {
        $('#home_results_table').hide();
        $('#away_results_table').show();
    }
    else {
        $('#away_results_table').hide();
        $('#home_results_table').show();
    };
}


function raw_get_years() {

    var group = $('select[name=group]').find(":selected").text();
    var league = $('select[name=league]').find(":selected").text();

    if (group === '') {
        $('input[name=year]').attr('disabled', 'disabled');
    }
    else {
        $.post('/years_update', {
            grp: group,
            lea: league
        }).done(function (data) {

            $('#year').html('');

            for (var i in data.years) {

                function year_appender(selector) {

                    $(selector)
                        .append('<option value="' + data.years[i] + '">' + data.years[i] + '</option>')
                }
                year_appender('#year');
            }

            $('select[name=year]').removeAttr('disabled');
            $('button[type=submit]').removeAttr("disabled");
            $("#error").text('');
            
        }); 
    };
}



function raw_data_check() {

    var group  = $('select[name=group]').find(":selected").text();
    var league = $('select[name=league]').find(":selected").text();
    var year   = $('select[name=year]').find(":selected").text();

    if (league && group && year !== "") {
        $("#error").text('');
        $('button[type=submit]').removeAttr("disabled");
    }
    else {
        $("#error").text("Some field is missing data");
        $('button[type=submit]').attr('disabled', 'disabled');
    };

}



function scroll_right_side_bar() {

    var state = $('#hide_right_side').html();

    if (state === "Show side bar") {
        $('#hide_right_side').html('Hide side bar');
        $('#right_side_bar').css('margin-right', '0');
        var right_bar_width = $("#right_side_bar").width();
        var left_bar_width  = $("#left_side_bar").width();
        var window_width    = $(window).width();
        var new_content_width   = window_width - right_bar_width - left_bar_width - 50;
        $("#content").css("width", new_content_width+'px');
    }
    else {
        $('#hide_right_side').html('Show side bar');
        $('#right_side_bar').css('margin-right', '-25rem');
        var left_bar_width  = $("#left_side_bar").width();
        var window_width    = $(window).width();
        var new_content_width   = window_width - left_bar_width - 50;
        $("#content").css("width", new_content_width+'px');
    };
}



function varying_type_change() {
    var type_selected = $('select[name=varying_type]').find(":selected").val();
    if (type_selected !== '0' & type_selected !== '3') {
        $('input[name=varying_value]').removeAttr("disabled");
        $('input[name=number_of_games]').removeAttr("disabled");
    }
    else if (type_selected === '3') {
        $('input[name=varying_value]').removeAttr("disabled");
        $('input[name=number_of_games]').removeAttr("disabled");
    }
    else {
        $('input[name=varying_value]').attr('disabled', 'disabled');
        $('input[name=number_of_games]').attr('disabled', 'disabled');
    }
}





function select_teams() {
    $("#test-form").css("display", "block");
}


function close_selection_team() {
    $('#mask, .select_teams_popup').fadeOut(300 , function() {
        $('#mask').remove();
    });

    $('.selected_teams_hidden').val($('.selected_teams').text());

    if ($('.selected_teams_hidden').val()) {

        var winter = $('.winter').css("text-decoration");
        if (winter === 'none') {
            $('.summer_winter').val('summer');
            var years = ['2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014'];
        }
        else {
            $('.summer_winter').val('winter');
            var years = ['2000-2001', '2001-2002', '2002-2003', '2003-2004', '2004-2005', '2005-2006', '2006-2007', '2007-2008', '2008-2009', '2009-2010', '2010-2011', '2011-2012', '2012-2013', '2013-2014', '2014-2015'];
        };
        $('#years').html('');
        $('#years_coeffs').html('');
        $('#mySlideContent').html('');

        if (years.length > 1) {
            $('#mySlideToggler').show();
        }
        else {
            $('#mySlideToggler').hide();
        }

        var first_year = years.slice(-1)
        $('#years').append('<input id="' + first_year + '" name="years" type="checkbox" value="' + first_year +  '"><label>' + first_year + '</label><br>');
        $('#years_coeffs').append('<input id="coefficient" name="' + first_year + '_coeff" type="text" autocomplete="off">');

        for (var i in years.slice(1)) {
        
            var year_div    = '<div class="large-7 text-left columns" id="years">'

            var year_input  = '<input id="' + years[i] + '" \
                               name="years" \
                               type="checkbox" \
                               value="' + years[i] + '">'

            var coeff_div   = '<div class="large-5 columns id="years_coeffs">'

            var coeff_input = '<input id="coefficient" name="' + years[i] + '_coeff" type="text" autocomplete="off">'

            $('#mySlideContent').prepend(year_div + year_input + '<label>' + years[i] + '</label><br></div>' + coeff_div + coeff_input + '</div>');
        };


        $('#button_save').removeAttr('disabled');
        $('#button_get').removeAttr('disabled');
    }

}



function open_select_teams() {

    $('a.select_teams_window').click(function() {
        var loginBox = $(this).attr('href');
        $(loginBox).fadeIn(300);
        var popMargTop = ($(loginBox).height() + 24) / 2; 
        var popMargLeft = ($(loginBox).width() + 24) / 2; 
        
        $(loginBox).css({ 
            'margin-top' : -popMargTop,
            'margin-left' : -popMargLeft
        });
        
        $('body').append('<div id="mask"></div>');
        $('#mask').fadeIn(300);
        
        return false;
        
    });
}