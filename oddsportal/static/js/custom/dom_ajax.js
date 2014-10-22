function get_template() {

    var selected_template = $('select[name=select_template]').find(":selected").val();
    var template_values   = JSON.parse(templates[selected_template])

    for (x in template_values){
        $('select[name=' + x + ']').val(template_values[x]);
        $('input[name='  + x + ']').val(template_values[x]);
    }

    if ($('input[name="odd_value"]').val() == ""){
        $("#error").text("Year or Stake field is empty");
        $('input[type=submit]').attr('disabled', 'disabled');
    }
    else {
        $('input[type=submit]').removeAttr('disabled');
        $("#error").html("")
    }
}



function save_template() {

    var template_name = $('input[name=template_name]').val();

    if (template_name === "") {
        alert('Put name');
        return
    }

    var form_playing_at_types  = $('select[name=form_playing_at_types]').find(":selected").val();
    var handicap    = $('select[name=handicap]').find(":selected").val();
    var strategy    = $('select[name=strategy]').find(":selected").val();
    var ou_values   = $('select[name=ou_values]').find(":selected").val();
    var game_part   = $('select[name=game_part]').find(":selected").val();
    var odds_type   = $('select[name=odds_type]').find(":selected").val();
    var odd_toggle  = $('input[name=odd_toggle]').val();
    var odd_value   = $('input[name=odd_value]').val();

    $.post('/save_template', {

        form_playing_at_types: form_playing_at_types,
        handicap:      handicap,
        strategy:      strategy,
        ou_values:     ou_values,
        game_part:     game_part,
        odds_type:     odds_type,
        odd_toggle:    odd_toggle,
        odd_value:     odd_value,
        template_name: template_name

    }).done(function(data) {

        templates = data.templates
        $('select[name=select_template]').empty();

            function templates_appender(selector) {
                $(selector).append('<option disabled selected> -- select a template -- </option>')
                $.each(data.templates, function (i, v) {
                    $(selector)
                        .append('<option>' + i + '</option>')
                });
            }
            templates_appender('select[name=select_template]');
            alert('Template saved');

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

    }).done(function(data) {
        alert('Database updated');
    }); 
}



function signIn() {
    $.post('/login', {
        username: $('input[name="username"]').val(),
        password: $('input[name="password"]').val()

    }).done(function(data) {
        if (data.result) {
            $("#error").text(data.result)
        }
        else {
            window.location.replace("/index")
        };
    });
};



function registration_form_check() {
    $.post('/reg_checker', {

        username: $('input[name="sign_up_username"]').val(),
        email:    $('input[name="sign_up_email"]').val()

    }).done(function(data) {

        if (data.username) {
            $("#username_icon_true").css('display', 'block');
            $("#username_icon_false").css('display','none');
        }
        else {
            $("#username_icon_true").css('display', 'none');
            $("#username_icon_false").css('display','block');
        };

        if (data.email) {
            $("#email_icon_true").css('display', 'block');
            $("#email_icon_false").css('display','none');
        }
        else {
            $("#email_icon_true").css('display', 'none');
            $("#email_icon_false").css('display','block');
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
        }).done(function(data) {
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
        }).done(function(data) {
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
    $('#years input:checked').each(function() {
        years_selected.push($(this).attr('value'));
    });
    
    odd_value = $('input[name="odd_value"]').val()

    if (odd_value && years_selected.length > 0) {
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
    if (handicap == 'Home/Draw/Away') {
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

    if (handicap == 'Over/Under') {
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