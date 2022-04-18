{% if calendar %}
var years_per_epoch = {}
var epoch_names = {}
var epoch_ids = []

{% for epoch in calendar["epochs"] %}
years_per_epoch[{{ epoch.id }}] = {{ epoch.years }};
epoch_names[{{ epoch.id }}] = "{{ epoch.name }}";
epoch_ids.push({{ epoch.id }});
{% endfor %}

var days_per_month = {}
var month_names = {}
var month_ids = []

{% for month in calendar["months"] %}
days_per_month[{{ month.id }}] = {{ month.days }};
month_names[{{ month.id }}] = "{{ month.name }}";
month_ids.push({{ month.id }});
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

function reload_epoch_picker() {
    $("#epoch_picker tr").remove();
    var epoch_val = $("#epoch").val();

    var items_per_row = 4;
    var epochs = {{ calendar['epochs']|length }};
    var row;

    for (var i = 0; i < epochs; i++) {
        if (i % items_per_row == 0) {
            row = $("<tr/>");
        }

        var cell = $('<td data-val="' + epoch_ids[i] + '">' + epoch_names[epoch_ids[i]] + '</td>');

        if (epoch_ids[i] == epoch_val) {
            cell.addClass("picker-selected");
        }

        cell.appendTo(row);

        if ((i % items_per_row) % (epochs - 1) == 0 || i == (epochs - 1)) {
            if (i == (epochs - 1) && (i % items_per_row) % (epochs - 1) != 0) {
                row_fillers = (items_per_row - ((i + 1) % items_per_row)) % items_per_row;

                for(var j = 0; j < row_fillers; j++) {
                    $("<td/>").appendTo(row);
                }
            }

            row.appendTo("#epoch_picker");
        }
    }

    $("#epoch_picker td[data-val]").click(function() {
        $("#epoch_picker td").removeClass("picker-selected");
        $("#epoch").val($(this).attr("data-val")).change();
        $(this).addClass("picker-selected");
    });
}

function init_epoch_picker() {
    $("<table/>").addClass("table picker").attr("id", "epoch_picker").insertAfter("#epoch");
    $("#epoch").hide();
    reload_epoch_picker();
}

function reload_month_picker() {
    $("#month_picker tr").remove();
    var month_val = $("#month").val();

    var items_per_row = 4;
    var months = {{ calendar['months']|length }};
    var row;

    for (var i = 0; i < months; i++) {
        if (i % items_per_row == 0) {
            row = $("<tr/>");
        }

        var cell = $('<td data-val="' + month_ids[i] + '">' + month_names[month_ids[i]] + '</td>');

        if (month_ids[i] == month_val) {
            cell.addClass("picker-selected");
        }

        cell.appendTo(row);

        if ((i % items_per_row) % (months - 1) == 0 || i == (months - 1)) {
            if (i == (months - 1) && (i % items_per_row) % (months - 1) != 0 ) {
                row_fillers = (items_per_row - ((i + 1) % items_per_row)) % items_per_row;

                for(var j = 0; j < row_fillers; j++) {
                    $("<td/>").appendTo(row);
                }
            }

            row.appendTo("#month_picker");
        }
    }

    $("#month_picker td[data-val]").click(function() {
        $("#month_picker td").removeClass("picker-selected");
        $("#month").val($(this).attr("data-val")).change();
        $(this).addClass("picker-selected");
    });
}

function init_month_picker() {
    $("<table/>").addClass("table picker").attr("id", "month_picker").insertAfter("#month");
    $("#month").hide();
    reload_month_picker();
}

function reload_day_picker() {
    $("#day_picker tr").remove();
    var month_val = $("#month").val();
    var day_val = $("#day").val();

    {% if calendar['days_per_week'] < 5 %}
    var items_per_row = 5;
    {% elif calendar['days_per_week'] > 12 %}
    var items_per_row = 12;
    {% else %}
    var items_per_row = {{ calendar['days_per_week'] }};
    {% endif %}

    items_per_row = Math.min(items_per_row, 12);
    var days = days_per_month[month_val];
    var row;

    for (var i = 1; i <= days; i++) {
        if (i % items_per_row == 1) {
            row = $("<tr/>");
        }

        var cell = $('<td data-val="' + i + '">' + i + '</td>');

        if (i == day_val) {
            cell.addClass("picker-selected");
        }

        cell.appendTo(row);

        if (i % items_per_row == 0 || i == days) {
            if (i == days && i % items_per_row != 0) {
                row_fillers = items_per_row - (i % items_per_row);

                for(var j = 0; j < row_fillers; j++) {
                    $("<td/>").appendTo(row);
                }
            }

            row.appendTo("#day_picker");
        }
    }

    $("#day_picker td[data-val]").click(function() {
        $("#day_picker td").removeClass("picker-selected");
        $("#day").val($(this).attr("data-val")).change();
        $(this).addClass("picker-selected");
    });
}

function init_day_picker() {
    $("<table/>").addClass("table picker").attr("id", "day_picker").insertAfter("#day");
    $("#day").hide();
    reload_day_picker();
}

$(document).ready(function() {
    $("#epoch").on('change', function(e) {
        gen_year_limits($(e.target).val());
    });

    $("#month").on('change', function(e) {
        gen_day_choices($(e.target).val());
        reload_day_picker();
    });

    $("#category").on('change', function(e) {
        set_category_border(category_colors[$(e.target).val()])
    });

    add_category_color();
    $("#category").selectpicker().parent().removeClass("form-select");
    set_category_border(category_colors[$("#category").val()])
    $("button[data-id=category]").css("height", "34px");

    init_epoch_picker();
    init_month_picker();
    init_day_picker();

    gen_year_limits($("#epoch").val());
    gen_day_choices($("#month").val());
});
{% else %}
alert("Calendar was included, but no calendar info object was provided");
{% endif %}