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

function toggleMapSidebar(editor) {
    if (mapVisible == false && (intRefVisible == true || mediaVisible == true)) {
        $("#intref-sidebar").hide();
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

/** NEW CODE STARTS HERE */

// add text to active editor window
// replaces current selection
function add_to_editor(text) {
  var cm = active_editor.codemirror;
  cm.replaceSelection(text);
}

// helper func
function markdown_image(text, url) {
  return "![" + text + "](" + url + ")";
}

// helper func
function markdown_link(text, url) {
  return "[" + text + "](" + url + ")";
}

// called after successful media upload via MediaUploader
// places buttons in the footer to directly add the new file to the editor
function on_successful_upload(new_media_info) {
  if (new_media_info) {
    var cm = active_editor.codemirror;
    var text = cm.getSelection() || new_media_info.name;

    var footer = media_uploader.get_footer();

    // button to add a link to the newly uploaded file
    var link_button = $('<button/>').attr("type", "button").addClass("btn btn-primary mr-auto").text("Add Link");
    link_button.click(function() {
      add_to_editor(markdown_link(text, new_media_info.serve_url));
      media_uploader.close_modal();
    });
    footer.prepend(link_button);

    if (new_media_info.is_image) {
      var thumbnail_button = $('<button/>').attr("type", "button").addClass("btn btn-primary").text("Add Thumbnail");
      thumbnail_button.click(function() {
        add_to_editor(markdown_image(text, new_media_info.thumbnail_url));
        media_uploader.close_modal();
      });
      footer.prepend(thumbnail_button);

      var direct_button = $('<button/>').attr("type", "button").addClass("btn btn-primary").text("Add Image");
      direct_button.click(function() {
        add_to_editor(markdown_image(text, new_media_info.serve_url));
        media_uploader.close_modal();
      });
      footer.prepend(direct_button);
    }
  } else {
    var err = $("<div/>").addClass("alert alert-danger").text("No information about the uploaded media could be retrieved.");
    media_uploader.get_body().append(err);
  }
}

// called after click on footer button of media sidebar
// builds and adds correct text to editor based on selected elements and clicked button
function insert_media(type, elements) {
  var out = "";
  var attr;
  var markdown_func;

  if (type == "thumbnail") {
    attr = "thumbnail-url";
    markdown_func = markdown_image;
  } else if (type == "image") {
    attr = "serve-url";
    markdown_func = markdown_image;
  } else if (type == "link") {
    attr = "serve-url";
    markdown_func = markdown_link;
  } else {
    console.log("unkown type " + type);
    return;
  }

  // keep current selection as text if there is only one element
  if (elements.length == 1) {
    var cm = active_editor.codemirror;
    var text = cm.getSelection() || $(elements[0]).attr("data-name");
    out = markdown_func(text, $(elements[0]).attr("data-" + attr));
  } else {
    for (var i = 0; i < elements.length; i++) {
      var elem = $(elements[i]);
      out += markdown_func(elem.attr("data-name"), elem.attr("data-" + attr));
      out += "\n";
    }
  }

  add_to_editor(out);
  media_sidebar.close_modal();
}

// footer buttons for media sidebar
var footer = [
  {
    button: $("<button/>").addClass("btn btn-primary").text("Add Thumbnail"),
    func: function(elements) {
      insert_media("thumbnail", elements);
    }
  },
  {
    button: $("<button/>").addClass("btn btn-primary").text("Add Image"),
    func: function(elements) {
      insert_media("image", elements);
    }
  },
  {
    button: $("<button/>").addClass("btn btn-primary").text("Add Link"),
    func: function(elements) {
      insert_media("link", elements);
    }
  }
];

var media_sidebar = new MediaModal("Insert file", "{{ url_for('media.sidebar_categories') }}", "media-sidebar", footer);
var media_uploader = new MediaUploader('{{ url_for("media.upload", ajax=1) }}', { onSuccess : on_successful_upload })

function toggleMediaSidebar(editor) {
  active_editor = editor;
  media_sidebar.open_modal();
}

function toggleMediaUploader(editor) {
  active_editor = editor;
  media_uploader.open_modal();
}

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

  var previewClasses = ["custom-markdown"];

  {% if current_user.markdown_phb_style == True %}
  previewClasses.push("phb-style")
  {% endif %}

  return {
    element: document.getElementById(id),
    previewClass: previewClasses,
    toolbar: toolb,
    spellChecker: false,
    status: false,
    autoDownloadFontAwesome: false,
    minHeight: '{{ current_user.editor_height }}px',
    onToggleFullScreen: function(fullscreen) {
      // hide navbar when going fullscreen
      $("#topnav").toggle(!fullscreen);
    },
    promptURLs: true
  }
}

function makeMarkdownEditor(id, withHeading=true) {
  new EasyMDE(generateMarkdownConfig(id, withHeading))
}
