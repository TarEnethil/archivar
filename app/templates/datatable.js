function makeDatatable(id) {
    var options = {
        autoWidth: false,
        order: []
    }

    $(id).DataTable(options);
}