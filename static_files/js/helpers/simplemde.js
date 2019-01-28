var intRefLoaded = false;
var intRefVisible = false;
var mediaLoaded = false;
var mediaVisible = false;

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

function toggleIntRefSidebar(editor) {
    if (intRefVisible == false && mediaVisible == true) {
        $("#media-sidebar").hide();
        mediaVisible = false;
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
    if (mediaVisible == false && intRefVisible == true) {
        $("#intref-sidebar").hide();
        intRefVisible = false;
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

var reference = {
    name: "insertReference",
    action: toggleIntRefSidebar,
    className: "fa fa-star fa-red",
    title: "Insert internal reference",
}

var media = {
    name: "insertMedia",
    action: toggleMediaSidebar,
    className: "fa fa-image fa-red",
    title: "Insert media"
}

function generateSMDEConfig(id, withHeading=true) {
    var toolb = ["bold", "italic", "heading-1", "heading-2", "heading-3", "|", "unordered-list", "ordered-list", "|", "link", "image", "table", "horizontal-rule", "|", "side-by-side", "fullscreen", "guide", "|", reference, media];

    if (withHeading == false) {
        toolb = ["bold", "italic", "|", "unordered-list", "ordered-list", "|", "link", "image", "table", "horizontal-rule", "|", "side-by-side", "fullscreen", "guide", "|", reference, media];
    }

    return {
        element: document.getElementById(id),
        toolbar: toolb,
        spellChecker: false,
        status: false
    }
}

function makeSMDE(id, withHeading=true) {
    new SimpleMDE(generateSMDEConfig(id, withHeading=true))
}