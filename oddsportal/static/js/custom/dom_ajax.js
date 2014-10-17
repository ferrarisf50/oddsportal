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