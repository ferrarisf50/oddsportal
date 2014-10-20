function get_template() {

    var selected_template = $('select[name=select_template]').find(":selected").val();
    var template_values   = JSON.parse(templates[selected_template])

    for (x in template_values){
        $('select[name=' + x + ']').val(template_values[x]);
        $('input[name='  + x + ']').val(template_values[x]);
    }

    if ($('input[name="odd_value"]').val() === ""){
        $("#error").text("Year or Stake field is empty");
        $('input[type=submit]').attr('disabled', 'disabled');
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