var loaded = false;
var visible = false;

function loadResource(editor, category, url, fake_url) {
    var list = $("#thinglist");

    console.log("called with " + category + ":::" + url + ":::"+ fake_url);

    $.getJSON(url, function(data) {
        $("<li/>").addClass("category").text(category).appendTo(thinglist).appendTo();
        console.log(data);

        for (var i in data) {
            var listitem = $("<li/>").addClass("thing").text(data[i][1]).attr("data-url", fake_url.replace("0", data[i][0])).appendTo(list);

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

        $(".close-link-sidebar").click(function() {
            sidebar.hide();
            visible = false;
        });

        var toLoad = [  { cat: "Characters", json_url: "{{ url_for('character.sidebar') }}", fake_url: "{{ url_for('character.view', id=0) }}" },
                        { cat: "Parties", json_url: "{{ url_for('party.sidebar') }}", fake_url: "{{ url_for('party.view', id=0) }}"},
                        { cat: "Sessions", json_url: "{{ url_for('session.sidebar') }}", fake_url: "{{ url_for('session.view', id=0) }}"},
                        { cat: "Wiki", json_url: "{{ url_for('wiki.sidebar') }}", fake_url: "{{ url_for('wiki.view', id=0) }}"} ];

        console.log(toLoad);

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

reference = {
    name: "insertReference",
    action: toggleSidebar,
    className: "fa fa-star fa-red",
    title: "Insert internal reference",
}

function generateSMDEConfig(id) {
    return {
        element: document.getElementById(id),
        toolbar: ["bold", "italic", "heading-1", "heading-2", "heading-3", "|", "quote", "unordered-list", "ordered-list", "|", "link", "image", "table", "horizontal-rule", "|", "side-by-side", "fullscreen", "guide", "|", reference],
        spellChecker: false,
        status: false
    }
}