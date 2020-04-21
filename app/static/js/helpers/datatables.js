function makeDatatable(id, threshold=11, items_per_page=10) {
    obj_id = "#" + id

    if ($(obj_id + " > tbody > tr").length >= threshold) {
        var options = {
            autoWidth: false,
            order: [],
            pageLength: items_per_page
        }

        $(obj_id).DataTable(options);
    }
}