function makeDeleteLink(id, itemname) {
    $("#" + id).click(function(e) {
        e.preventDefault();
        var button = $(this);

        bootbox.confirm("Are you sure you want to delete '" + itemname + "'?", function(result) {
            if (result) {
                $(button).unbind('click');
                e.currentTarget.click();
            }
        });
    });
}

var member_select;

function onSelectParty(id) {
    var name = $("#associated_parties option[value=" + id + "]").text();

    if (name) {
        var unselected_members = $("#default_participants optgroup[label='" + name + "'] option").not(":selected");

        if (unselected_members.length > 0) {
            bootbox.confirm("Do you want to add the party members of '" + name + "' to the default participants?", function(result) {
                if (result) {
                    $(unselected_members).each(function() {
                        member_select.multiSelect('select', $(this).attr("value"));
                    });
                }
            });
        }
    }
}

function onDeselectParty(id) {
    var name = $("#associated_parties option[value=" + id + "]").text();

    if (name) {
        var selected_members = $("#default_participants optgroup[label='" + name + "'] option:selected");

        if (selected_members.length > 0) {
            bootbox.confirm("Do you want to remove the party members of '" + name + "' from the default participants?", function(result) {
                if (result) {
                    $(selected_members).each(function() {
                        member_select.multiSelect('deselect', $(this).attr("value"));
                    });
                }
            });
        }
    }
}