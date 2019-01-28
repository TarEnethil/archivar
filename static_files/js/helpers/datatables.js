function makeDatatable(id, items_per_page=10) {
    var options = {
        autoWidth: false,
        order: [],
        pageLength: items_per_page
    }

    $("#" + id).DataTable(options);
}