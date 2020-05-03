var intRefLoaded = false;
var intRefVisible = false;
var mediaLoaded = false;
var mediaVisible = false;
var mapLoaded = false;
var mapVisible = false;

var img_extensions = ["png", "gif", "jpg", "jpeg"];

var active_editor = undefined;

function intRefLoadResource(editor, category, url, fake_url) {
    var list = $("#intref-sidebar .itemlist");
    var listitem = undefined;

    $.getJSON(url, function(data) {
        var x = $("<li/>").addClass("category").text(category).appendTo(list);

        for (var i in data) {
            if (listitem == undefined)
                listitem = $("<li/>").appendTo(list);
            else
                listitem = $("<li/>").insertAfter(listitem);

            listitem.addClass("thing").text(data[i][1]).attr("data-url", fake_url.replace("0", data[i][0]));

            if (data[i][2] == false) {
                listitem.addClass("invis");
            }

            $(listitem).click(function() {
                insertReference(editor, $(this).text(), $(this).attr("data-url"));
            });
        }
    });
}

function mediaLoadResource(editor, category, url) {
    var list = $("#media-sidebar .itemlist");
    var listitem = undefined;

    $.getJSON(url, function(data) {
        if ($.isEmptyObject(data))
            return;

        var x = $("<li/>").addClass("category").text(category).appendTo(list);

        for (var i in data) {
            if (listitem == undefined)
                listitem = $("<li/>").appendTo(list);
            else
                listitem = $("<li/>").insertAfter(listitem);

            listitem.addClass("thing").text(data[i].name).attr("data-text", data[i].name).attr("data-filename", data[i].filename);
            listitem.attr("data-file-ext", data[i].file_ext).attr("data-id", data[i].id);

            if (data[i].is_visible == false) {
                listitem.addClass("invis");
            }

            $("<span/>").addClass("file-ext").text("[" + data[i].file_ext + "] ").prependTo(listitem);

            $(listitem).click(function() {
                insertMedia(editor, $(this).attr("data-text"), $(this).attr("data-id"), $(this).attr("data-filename"), $(this).attr("data-file-ext"));
            });
        }
    });
}

function mapLoadResource(editor, category, url) {
    var fake_url = "{{ url_for('map.view_with_node', id=-1, n_id=0) }}".replace("-1", category.id);
    var list = $("#map-sidebar .itemlist");
    var listitem = undefined;

    $.getJSON(url, function(data) {
        if ($.isEmptyObject(data))
            return;

        var x = $("<li/>").addClass("category").text(category.name).appendTo(list);

        for (var i in data) {
            if (listitem == undefined)
                listitem = $("<li/>").appendTo(list);
            else
                listitem = $("<li/>").insertAfter(listitem);

            listitem.addClass("thing").text(data[i].name).attr("data-url", fake_url.replace("0", data[i].id));

            if (data[i].visible == false) {
                listitem.addClass("invis");
            }

            $(listitem).click(function() {
                insertReference(editor, $(this).text(), $(this).attr("data-url"));
            });
        }
    });
}

function toggleIntRefSidebar(editor) {
    if (intRefVisible == false && (mediaVisible == true || mapVisible == true)) {
        $("#media-sidebar").hide();
        $("#map-sidebar").hide();
        mediaVisible = false;
        mapVisible = false;
    }

    if (intRefLoaded == false) {
        var sidebar = $("#intref-sidebar");

        // load and show
        intRefLoaded = true;
        sidebar.show();
        intRefVisible = true;

        $("#intref-sidebar .close-link-sidebar").click(function() {
            sidebar.hide();
            intRefVisible = false;
        });

        var toLoad = [  { cat: "Characters", json_url: "{{ url_for('character.sidebar') }}", fake_url: "{{ url_for('character.view', id=0) }}" },
                        { cat: "Events", json_url: "{{ url_for('event.sidebar') }}", fake_url: "{{ url_for('event.view', id=0) }}" },
                        { cat: "Parties", json_url: "{{ url_for('party.sidebar') }}", fake_url: "{{ url_for('party.view', id=0) }}"},
                        { cat: "Sessions", json_url: "{{ url_for('session.sidebar') }}", fake_url: "{{ url_for('session.view', id=0) }}"},
                        { cat: "Wiki", json_url: "{{ url_for('wiki.sidebar') }}", fake_url: "{{ url_for('wiki.view', id=0) }}"} ];

        for (var i in toLoad) {
            intRefLoadResource(editor, toLoad[i].cat, toLoad[i].json_url, toLoad[i].fake_url);
        }

        $("#filter_things").on("keyup", function() {
            var value = $(this).val().toLowerCase();

            $("#intref-sidebar .itemlist li.thing").filter(function() {
                $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
            });
        });
    } else {
        if (intRefVisible == false) {
            $("#intref-sidebar").show();
            intRefVisible = true;
        } else {
            $("#intref-sidebar").hide();
            intRefVisible = false;
        }
    }

    active_editor = editor;
}

function toggleMediaSidebar(editor) {
    if (mediaVisible == false && (intRefVisible == true || mapVisible == true)) {
        $("#intref-sidebar").hide();
        $("#map-sidebar").hide();
        intRefVisible = false;
        mapVisible = false;
    }

    if (mediaLoaded == false) {
        // LOAD MEDIA
        var sidebar = $("#media-sidebar");

        // load and show
        mediaLoaded = true;
        sidebar.show();
        mediaVisible = true;

        $("#media-sidebar .close-link-sidebar").click(function() {
            sidebar.hide();
            mediaVisible = false;
        });

        $.getJSON("{{ url_for('media.sidebar_categories') }}", function(data) {
            var url = "{{ url_for('media.sidebar', c_id='0') }}";
            for (var i in data) {
                mediaLoadResource(editor, data[i].name, url.replace("0", data[i].id));
            }
        });

        $("#filter_media").on("keyup", function() {
            var value = $(this).val().toLowerCase();

            $("#media-sidebar .itemlist li.thing").filter(function() {
                $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
            });
        });
    } else {
        if (mediaVisible == false) {
            $("#media-sidebar").show();
            mediaVisible = true;
        } else {
            $("#media-sidebar").hide();
            mediaVisible = false;
        }
    }

    active_editor = editor;
}

function toggleMapSidebar(editor) {
    if (mapVisible == false && (intRefVisible == true || mediaVisible == true)) {
        $("#intref-sidebar").hide();
        $("#media-sidebar").hide();
        intRefVisible = false;
        mediaVisible = false;
    }

    // LOAD MAP NODES
    var sidebar = $("#map-sidebar");

    if (mapLoaded == false) {
        // load and show
        mapLoaded = true;
        sidebar.show();
        mapVisible = true;

        $("#map-sidebar .close-link-sidebar").click(function() {
            sidebar.hide();
            mapVisible = false;
        });

        $.getJSON("{{ url_for('map.sidebar_maps') }}", function(data) {
            var url = "{{ url_for('map.sidebar', m_id='0') }}";
            for (var i in data) {
                mapLoadResource(editor, data[i], url.replace("0", data[i].id));
            }
        });

        $("#filter_mapnodes").on("keyup", function() {
            var value = $(this).val().toLowerCase();

            $("#map-sidebar .itemlist li.thing").filter(function() {
                $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
            });
        });
    } else {
        if (mapVisible == false) {
            $("#map-sidebar").show();
            mapVisible = true;
        } else {
            $("#map-sidebar").hide();
            mapVisible = false;
        }
    }

    active_editor = editor;
}

function insertReference(editor, name, url) {
    var cm = active_editor.codemirror;
    var stat = active_editor.getState(cm);
    var options = active_editor.options;
    var oldText = cm.getSelection() || name;

    var output = "[linktext](url)";

    output = output.replace("linktext", oldText);
    output = output.replace("url", url);
    cm.replaceSelection(output);
}

function insertMedia(editor, name, id, filename, file_ext) {
    var cm = active_editor.codemirror;
    var stat = active_editor.getState(cm);
    var options = active_editor.options;
    var oldText = cm.getSelection() || name;

    var output = "[linktext](url)";
    var url = ""

    if ($("#use_direct_links").prop("checked")) {
        url = "{{ url_for('media.serve_file', filename='0') }}".replace("0", filename);
    } else {
        url = "{{ url_for('media.view', id=0) }}".replace("0", id);
    }

    if ($("#use_embedded_images").prop("checked") && img_extensions.indexOf(file_ext) >= 0) {
        // embed image enforces the use of serve_file endpoint
        url = "{{ url_for('media.serve_file', filename='0') }}".replace("0", filename);
        output = "!" + output;
    }

    output = output.replace("linktext", oldText);
    output = output.replace("url", url);

    cm.replaceSelection(output);
}

function insertNewMedia(text) {
    var cm = active_editor.codemirror;
    cm.replaceSelection(text);
}

// after successful media upload via MediaUploader
// places buttons in the footer to directly add the new file to the editor
function on_success(new_media_info) {
    if (new_media_info) {
        var cm = active_editor.codemirror;
        var text = cm.getSelection() || new_media_info.name;

        var footer = media_uploader.get_footer();

        // button to add a link to the newly uploaded file
        var link_button = $('<button/>').attr("type", "button").addClass("btn btn-primary mr-auto").text("Add Link");
        link_button.click(function() {
            insertNewMedia("[" + text + "](" + new_media_info.serve_url + ")");
            media_uploader.close_modal();
        });
        footer.prepend(link_button);

        if (new_media_info.is_image) {
            var thumbnail_button = $('<button/>').attr("type", "button").addClass("btn btn-primary").text("Add Thumbnail");
            thumbnail_button.click(function() {
                insertNewMedia("![" + text + "](" + new_media_info.thumbnail_url + ")");
                media_uploader.close_modal();
            });
            footer.prepend(thumbnail_button);

            var direct_button = $('<button/>').attr("type", "button").addClass("btn btn-primary").text("Add Image");
            direct_button.click(function() {
                insertNewMedia("![" + text + "](" + new_media_info.serve_url + ")");
                media_uploader.close_modal();
            });
            footer.prepend(direct_button);
        }
    } else {
        var err = $("<div/>").addClass("alert alert-danger").text("No information about the uploaded media could be retrieved.");
        media_uploader.get_body().append(err);
    }
}

// global var
var media_uploader = new MediaUploader('{{ url_for("media.upload", ajax=1) }}', { onSuccess : on_success })

function toggleMediaUploader(editor) {
    active_editor = editor;

    media_uploader.open_modal();
}

$("#media_upload").click(function() {
    m.open_modal();
});

var reference = {
    name: "insertReference",
    action: toggleIntRefSidebar,
    className: "fas fa-star text-primary",
    title: "Insert Reference",
}

var media = {
    name: "insertMedia",
    action: toggleMediaSidebar,
    className: "fas fa-images text-primary",
    title: "Insert Media File"
}

var maps = {
    name: "insertMapNode",
    action: toggleMapSidebar,
    className: "fas fa-map-marker-alt text-primary",
    title: "Insert Location"
}

var upload = {
    name: "uploadMedia",
    action: toggleMediaUploader,
    className: "fas fa-file-upload text-primary",
    title: "Upload File"
}

function generateMarkdownConfig(id, withHeading=true) {
    var toolb = ["bold", "italic", "heading-1", "heading-2", "heading-3", "|", "unordered-list", "ordered-list", "|", "link", "image", "table", "horizontal-rule", "|", "side-by-side", "fullscreen", "guide", "|", reference, media, maps, "|", upload];

    if (withHeading == false) {
        toolb = ["bold", "italic", "|", "unordered-list", "ordered-list", "|", "link", "image", "table", "horizontal-rule", "|", "side-by-side", "fullscreen", "guide", "|", reference, media, maps, upload];
    }

    return {
        element: document.getElementById(id),
        toolbar: toolb,
        spellChecker: false,
        status: false,
        autoDownloadFontAwesome: false,
        minHeight: '{{ current_user.editor_height }}px',
        onToggleFullScreen: function(fullscreen) {
            // hide navbar when going fullscreen
            $("#topnav").toggle(!fullscreen);
        }
    }
}

function makeMarkdownEditor(id, withHeading=true) {
    new EasyMDE(generateMarkdownConfig(id, withHeading))
}