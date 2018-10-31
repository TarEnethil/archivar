var loaded = false;
var visible = false;

function loadResource(editor, category, url, fake_url) {
    var list = $("#thinglist");
    var listitem = undefined;

    $.getJSON(url, function(data) {
        $("<li/>").addClass("category").text(category).appendTo(thinglist);

        for (var i in data) {
            if (listitem == undefined)
                listitem = $("<li/>").addClass("thing").text(data[i][1]).attr("data-url", fake_url.replace("0", data[i][0])).appendTo(list);
            else
                listitem = $("<li/>").addClass("thing").text(data[i][1]).attr("data-url", fake_url.replace("0", data[i][0])).insertAfter(listitem);

            if (data[i][2] == false) {
                listitem.addClass("invis");
            }

            $(listitem).click(function() {
                insertReference(editor, $(this).text(), $(this).attr("data-url"));
            });
        }
    });
}

function toggleSidebar(editor) {
    if (loaded == false) {
        var sidebar = $("#editor-sidebar");

        // load and show
        loaded = true;
        sidebar.show();
        visible = true;

        $("#editor-sidebar .close-link-sidebar").click(function() {
            sidebar.hide();
            visible = false;
        });

        var toLoad = [  { cat: "Characters", json_url: "{{ url_for('character.sidebar') }}", fake_url: "{{ url_for('character.view', id=0) }}" },
                        { cat: "Events", json_url: "{{ url_for('event.sidebar') }}", fake_url: "{{ url_for('event.view', id=0) }}" },
                        { cat: "Parties", json_url: "{{ url_for('party.sidebar') }}", fake_url: "{{ url_for('party.view', id=0) }}"},
                        { cat: "Sessions", json_url: "{{ url_for('session.sidebar') }}", fake_url: "{{ url_for('session.view', id=0) }}"},
                        { cat: "Wiki", json_url: "{{ url_for('wiki.sidebar') }}", fake_url: "{{ url_for('wiki.view', id=0) }}"} ];

        for (var i in toLoad) {
            loadResource(editor, toLoad[i].cat, toLoad[i].json_url, toLoad[i].fake_url);
        }

        $("#filter_things").on("keyup", function() {
            var value = $(this).val().toLowerCase();

            $("#thinglist li.thing").filter(function() {
                $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
            });
        });
    }

    if (visible == false) {
        $("#editor-sidebar").show();
        visible = true;
    }
}

function insertReference(editor, name, url) {
    var cm = editor.codemirror;
    var stat = editor.getState(cm);
    var options = editor.options;
    var oldText = cm.getSelection() || name;

    var output = "[linktext](url)";

    output = output.replace("linktext", oldText);
    output = output.replace("url", url);
    cm.replaceSelection(output);
}

var reference = {
    name: "insertReference",
    action: toggleSidebar,
    className: "fa fa-star fa-red",
    title: "Insert internal reference",
}

function generateSMDEConfig(id, withHeading=true) {
    var toolb = ["bold", "italic", "heading-1", "heading-2", "heading-3", "|", "unordered-list", "ordered-list", "|", "link", "image", "table", "horizontal-rule", "|", "side-by-side", "fullscreen", "guide", "|", reference];

    if (withHeading == false) {
        toolb = ["bold", "italic", "|", "unordered-list", "ordered-list", "|", "link", "image", "table", "horizontal-rule", "|", "side-by-side", "fullscreen", "guide", "|", reference];
    }

    return {
        element: document.getElementById(id),
        toolbar: toolb,
        spellChecker: false,
        status: false
    }
}