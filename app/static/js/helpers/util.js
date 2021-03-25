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