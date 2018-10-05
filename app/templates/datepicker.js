{% if calendar %}
var years_per_epoch = {}

{% for epoch in calendar["epochs"] %}
years_per_epoch[{{ epoch.id }}] = {{ epoch.years }}
{% endfor %}

var days_per_month = {}

{% for month in calendar["months"] %}
days_per_month[{{ month.id }}] = {{ month.days }}
{% endfor %}

var category_colors = {}

{% for cat in calendar["categories"] %}
category_colors[{{ cat.id }}] = "{{ cat.color }}";
{% endfor %}

function gen_year_limits(epoch_id) {
    num_years = years_per_epoch[epoch_id];
    if (num_years == undefined) {
        alert("Could not generate limits for epoch-id " + epoch_id + ".");
        return;
    }

    var plh = "Placeholder";

    if (num_years != 0) {
        old_val = $("#year").val();
        $("#year").attr("min", 1);
        $("#year").attr("max", num_years);

        plh = "Range 1 - " + num_years;

        if (old_val > num_years) {
            $("#year").val(num_years);
        }
    } else {
        $("#year").attr("min", 1);
        $("#year").removeAttr("max");
        plh = "Starting at 1";
    }

    $("#year").attr("placeholder", plh);
    $("label[for=year]").html("Year (" + plh + ")");
}

function gen_day_choices(month_id) {
    num_days = days_per_month[month_id];
    if (num_days == undefined) {
        alert("Could not generate the day-choices for month_id " + month_id + ".");
        return;
    }

    old_val = $("#day").val();
    $("#day option").remove();

    for (var i = 1; i <= num_days; i++) {
        $("#day").append(new Option(i, i));
    }

    if (old_val <= num_days) {
        $("#day").val(old_val);
    }
}

function add_category_color() {
    $("#category option").each(function() {
        $(this).attr("style", "border-left: 10px solid " + category_colors[$(this).attr("value")]);
    });
}

function set_category_border(color) {
    $("#category").next().css('border-left', '10px solid ' + color)
}

$("#epoch").on('change', function(e) {
    gen_year_limits($(e.target).val());
});

$("#month").on('change', function(e) {
    gen_day_choices($(e.target).val());
});

$("#category").on('change', function(e) {
    set_category_border(category_colors[$(e.target).val()])
});

add_category_color();
$("#category").selectpicker();
set_category_border(category_colors[$("#category").val()])

gen_year_limits($("#epoch").val());
gen_day_choices($("#month").val());

{% else %}
alert("Calendar was included, but no calendar info object was provided");
{% endif %}