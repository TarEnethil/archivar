function makeDatatable(id, opts) {
    obj_id = "#" + id

    if (opts == undefined) {
        opts = {}
    }

    if (opts.threshold == undefined) {
        opts.threshold = 11;
    }

    if (opts.items_per_page == undefined) {
        opts.items_per_page = 10;
    }

    if (opts.has_dates == undefined) {
        opts.has_dates = false;
    }

    if ($(obj_id + " > tbody > tr").length >= opts.threshold) {
        var options = {
            autoWidth: false,
            order: [],
            pageLength: opts.items_per_page
        }

        var table = $(obj_id).DataTable(options);

        // need to render moment-js timestamps after pagination, search, sort, etc ...
        if (opts.has_dates) {
            table.on( 'draw', function () {
                flask_moment_render_all();
            });
        }
    }
}