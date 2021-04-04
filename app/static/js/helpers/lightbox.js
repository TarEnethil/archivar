function lightbox(src, title=undefined) {
    $("#lightbox .modal-dialog img").attr("src", src);
    if (title != undefined) {
        $("#lightbox .modal-header h5").text(title);
    }
    $("#lightbox").modal("show");
}

$(document).ready(function() {
    $(".custom-markdown").find("img").each(function() {
        var url = $(this).attr("src");

        if (url.indexOf("/media/serve") > -1) {
            $(this).addClass("lightbox-img");

            if (url.indexOf("/media/serve-thumb") > -1) {
                $(this).attr("data-full-url", url.replace("serve-thumb", "serve"));
            }
        }
    });


    $(".lightbox-img").click(function() {
        var url = $(this).attr("data-full-url");
        var title = $(this).attr("data-title");

        if (url == undefined || url == '') {
            url = $(this).attr("src");
        }

        if (title == undefined || title == '') {
            title = undefined;
        }

        lightbox(url, title);
    });

    $("#lightbox").on("hide.bs.modal", function(e) {
        $(this).find(".modal-dialog img").attr("src", "");
        $(this).find(".modal-header h5").text("");
    });
});