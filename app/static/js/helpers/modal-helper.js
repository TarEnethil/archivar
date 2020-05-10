/*
 * Base class to create a Modal which displays information retrieved asynchronously.
 * It queries a given endpoint for categories, and subsequently queries each category for the items it should display.
 * How an element is displayed must be defined in the derived class.
 * Provides the possibility to customize footer button / actions.
 */
class AsyncCategoryLoader {
  /* title: string displayed in the modal header
   * url: where to load the categories from (expects json-obj ["categories"] with name, url and id fields)
   * id: html id attribute (must be unique)
   * footer info: array of { button, func }, where func will get called with an array of selected elements when button is clicked
   * opts:
   *    - parent: parent-element for the modal
   *    - modal_opts: additional classes for the modal-dialog
   *    - allow_multiselect: whether or not to allow multiple selected elements at once
   */
  constructor(title, url, id, footer_info, opts) {
    this.title = title;
    this.query_url = url;
    this.modal_id = id;
    this.footer_info = footer_info;

    this.parent = "body";
    this.modal_opts = "";
    this.allow_multiselect = true;

    this.loaded = false;
    this.setup = false;

    // set opts
    if (opts) {
      if (opts.hasOwnProperty("parent"))
        this.parent = opts.parent;

      if (opts.hasOwnProperty("modal_opts"))
        this.modal_opts = opts.modal_opts;

      if (opts.hasOwnProperty("allow_multiselect"))
        this.allow_multiselect = opts.allow_multiselect;
    }

    // add modal to DOM
    this.insert_modal();

    this.header = "#" + this.modal_id + " .modal-header";
    this.body = "#" + this.modal_id + " .modal-body";
    this.footer = "#" + this.modal_id + " .modal-footer";
  }

  // insert modal into DOM inside of this.parent
  // only done once per instance
  insert_modal() {
    if (!$("#" + this.modal_id).length) {
      $(this.parent).append('<div class="modal" id="' + this.modal_id + '" data-backdrop="static"> \
        <div class="modal-dialog ' + this.modal_opts + '"> \
          <div class="modal-content"> \
            <div class="modal-header"> \
              <h5 class="modal-title"></h5> \
              <form class="form-inline ml-auto"> \
                <input type="search" placeholder="Search" class="form-control filter-input" /> \
                <button type="button" class="close" data-dismiss="modal"> \
                  <span class="fas fa-times"></span> \
                </button> \
              </form> \
            </div> \
            <div class="modal-body"></div> \
            <div class="modal-footer"> \
              <p class="mr-auto left-footer"> \
                Elements selected: <span class="active-elem-count">0</span> | deselect: \
                <a href="#" id="deselect-all">all</a> &bullet; \
                <a href="#" id="deselect-hidden">hidden</a> | \
                <a href="#" id="refresh">refresh</a> \
              </p> \
            </div> \
          </div> \
        </div> \
      </div>');
    }
  }

  // open modal dialog
  // on first open, load everything and hook everyhing up
  open_modal() {
    var _this = this;
    var modal_id = "#" + _this.modal_id;

    // not loaded -> load categories
    if (!this.loaded) {
      $.ajax({
        type: "POST",
        url: _this.query_url,
        success: function(resp) {
          _this.loaded = true;
          resp.categories.forEach(function(category, index) {
            _this.load_category(category);
          });
        },
        error: function(resp, textStatus, errorThrown) { //< called when the server reports an error
          _this.loaded = false;
          $(_this.body).html($("<p/>").addClass("alert alert-danger").text("A server-side error occured while loading the categories. If this problem consists, please contact the administrator. (Hints: " + textStatus + ", " + errorThrown + ")"));
        }
      });
    }

    if (!this.setup) {
      this.setup = true;
      this.setup_header();
      this.setup_footer();
    }

    /* everytime this is opened:
     * - clear filter
     * - deselect everything
    */
    $(this.header + " .filter-input").val("");
    this.clear_active_elements();
    $(modal_id).modal("show");
  }

  // load the content for a single category
  load_category(category_data) {
    var _this = this;
    var modal_id = "#" + _this.modal_id;

    $.ajax({
      type: "POST",
      url: category_data.url,
      success: function(resp) {
        // create container for this category
        var cat_container = $("<div/>").addClass("m-2 modal-category").attr("id", "cat-" + category_data.id).append($("<h5/>").text(category_data.name).append($("<span/>").addClass("cat-count").text(" (0)"))).appendTo($(_this.body));

        // insert data into container
        _this.insert_data(resp.data, cat_container);

        // display element count for this category
        _this.update_count_for_category(cat_container);

        // hook up onclick-event for elements
        $(cat_container).find(".single-modal-element").click(function() {
            _this.elem_clicked($(this));
        })
      },
      error: function(resp, textStatus, errorThrown) { //< called when the server reports an error
        _this.loaded = false;
        $(modal_id + " .modal-body").html($("<p/>").addClass("alert alert-danger").text("A server-side error occured while loading the category '" + category_data.name + "'. If this problem consists, please contact the administrator. (Hints: " + textStatus + ", " + errorThrown + ")"));
      }
    });
  }

  // insert data into category
  insert_data(data, parent) {
    var _this = this;
    var row = $("<div/>").addClass("row align-items-end");

    data.forEach(function(elem, index) {
      // insert_single_data is implemented in derived class
      var single_data = _this.insert_single_data(elem);
      single_data = _this.tag_data(single_data, elem);
      row.append(single_data);
    });

    parent.append(row);
  }

  // add data-*-fields to the element
  // done as extra function so new items can be added externally
  tag_data(data, tags) {
    var tagged_data = $(data);
    tagged_data.addClass("single-modal-element");

    // copy every member of the element into data-* attributes for usage outside
    for (var key in tags) {
      tagged_data.attr("data-" + key, tags[key]);
    }

    return tagged_data;
  }

  // update how many (visible) elements are displayed in a category
  update_count_for_category(category) {
    var count = $(category).find(".single-modal-element").filter(function() {
        return $(this).css("display") !== 'none';
    }).length;

    $(category).find(".cat-count").text(" (" + count + ")");
  }

  // on-click event for elements, toggles active state and updates counters
  elem_clicked(elem) {
    if ($(elem).hasClass("active")) {
      $(elem).removeClass("active");
    } else {
      if (this.allow_multiselect == false) {
        // deselect-all if multiselect is disallowed
        this.get_active_elements().each(function() {
          $(this).removeClass("active");
        });
      }
      $(elem).addClass("active");
    }

    this.update_active_count();
  }

  // display how many elements are selected in the footer
  // counts hidden / filtered elements separately
  update_active_count() {
    var all = this.get_active_elements();
    var full_count = all.length;
    var count_str = full_count;

    var hidden = $(this.body).find(".single-modal-element.active").filter(function() {
        return $(this).css("display") === 'none';
    }).length;

    if (hidden > 0) {
      count_str += " (" + hidden + " hidden)";
    }

    $(this.footer).find(".active-elem-count").text(count_str);

    this.update_footer_buttons(all);
  }

  // enable/disable buttons in footer based on the currently selected elements
  update_footer_buttons(active_elements) {
    var _this = this;

    if (!this.footer_info) {
      return;
    }

    this.footer_info.forEach(function(foo) {
      var enabled;

      // if a button has a custom enabled_func, use this
      if (foo.enabled_func) {
        enabled = foo.enabled_func(active_elements);
      } else {
      // no custom func -> simple logic: only enable if elements are selected
        if (active_elements.length > 0) {
          enabled = true;
        } else {
          enabled = false;
        }
      }

      // set button state
      if (enabled) {
        $(foo.button).removeClass("disabled").removeAttr("disabled");
      } else {
        $(foo.button).addClass("disabled").attr("disabled", "disabled");
      }
    });
  }

  // get all currently selected elements
  get_active_elements() {
    return $(this.body).find(".single-modal-element.active");
  }

  // deselect all selected elements
  clear_active_elements() {
    $(this.get_active_elements()).each(function() {
      $(this).removeClass("active");
    });
    this.update_active_count();
  }

  // deselect all elements currently not shown because of filtering
  clear_active_hidden_elements() {
    $(this.get_active_elements()).each(function() {
      if ($(this).css("display") === 'none') {
        $(this).removeClass("active");
      }
    });
    this.update_active_count();
  }

  // close the modal
  close_modal() {
    $("#" + this.modal_id).modal("hide");
  }

  // set title and hook up filter form
  setup_header() {
    $(this.header + " h5").text(this.title);

    var _this = this;
    var modal_id = "#" + _this.modal_id;

    // setup filter form
    $(modal_id + " .filter-input").on("keyup", function() {
      var value = $(this).val().toLowerCase();

      $(modal_id + " .single-modal-element").filter(function() {
        // matches() is defined in the derived class
        $(this).toggle(_this.matches($(this), value));
      });

      // update category counters after filtering
      $(modal_id + " .modal-category").each(function() {
        _this.update_count_for_category(this);
      });

      // update selected-count after filtering
      _this.update_active_count();
    });
  }

  // display and hook up footer buttons and link
  setup_footer() {
    var _this = this;

    // hook up deselect-link
    $(_this.footer + " #deselect-all").click(function(e) {
      e.preventDefault();
      _this.clear_active_elements();
    });

    // hook up deselect-hidden-link
    $(_this.footer + " #deselect-hidden").click(function(e) {
      e.preventDefault();
      _this.clear_active_hidden_elements();
    });

    // set up refresh button
    $(_this.footer + " #refresh").click(function(e) {
      e.preventDefault();

      var sure = true;

      if (_this.get_active_elements().length > 0) {
        sure = confirm("If you refresh, your current selection will be lost. Continue?");
      }

      if (sure) {
        _this.loaded = false;
        $("#" + _this.modal_id + " .modal-body").empty();
        _this.open_modal();
      }
    });

    // set up custom buttons
    this.footer_info.forEach(function(foo) {
        // buttons spawn in a disabled state
        $(foo.button).addClass("footer-btn disabled").attr("disabled", "disabled");

        // fire this buttons function when its clicked
        $(foo.button).click(function() {
            foo.click_func(_this.get_active_elements());
        });

        $(_this.footer).append($(foo.button));
    });
  }
}

/*
 * A Modal to display all media files with image-thumbnails (if available).
 * Footer actions have to be added from outside
 * Uses:
 *  - add images to markdown editor
 *  - image picker
 */
class MediaModal extends AsyncCategoryLoader {
  /* title: string displayed in the modal header
   * url: where to load the media-categories from
   * id: html id attribute (must be unique)
   * footer info: array of { button, func }, where func will get called with an array of selected elements when button is clicked
   * opts:
   *    - parent: parent-element for the modal
   *    - modal_opts: additional classes for the modal-dialog
   *    - allow_multiselect: whether or not to allow multiple selected elements at once
   *    - media_upload_url: if given, a MediaUploader will be added to the Modal to upload files asynchronously
   */
  constructor(title, url, id, footer_info, opts) {
    if (!opts) {
        var opts = {};
    }

    if (!opts.modal_opts) {
        // default modal opts: extra large and scrollable
        opts.modal_opts = "modal-xl modal-dialog-scrollable";
    }

    super(title, url, id, footer_info, opts);

    // hook up MediaUploader if url is given
    // this works after super(), because setup_header() is only done in open_modal()
    if (opts.media_upload_url) {
      var _this = this;

      // TODO: temporary function to refer to this, is it needed?
      var success = function(info) {
        _this.on_successful_upload(info);
      }

      this.media_uploader = new MediaUploader(opts.media_upload_url, _this.modal_id + "-upload-modal", { onSuccess : success });
    }
  }

  // matches a media file against a (lower-cased) search term
  // currently looks up name and filename, which means you can also easily filter by file extension
  matches(elem, value) {
    var match = $(elem).attr("data-name").toLowerCase().indexOf(value) > -1;
    match = match || $(elem).attr("data-filename").toLowerCase().indexOf(value) > -1;
    return match;
  }

  // how a single media file is displayed
  insert_single_data(file_data) {
    var elem;

    // images are displayed as <figures>
    if (file_data["is-image"] == true) {
      elem = $("<figure/>").addClass("p-1 figure mb-0");

      $("<img/>").addClass("thumbnail-small img-thumbnail mx-auto").attr("src", file_data["thumbnail-url"]).appendTo(elem);
      $("<figcaption/>").addClass("figure-caption text-center text-truncate").text(file_data.name).appendTo(elem);
    } else {
      // non-images are displayed as <p> with an icon (based on some light filetype logic)
      elem = $("<p/>").text(file_data.name).addClass("p-1 mx-auto figure-caption text-center text-truncate mb-0");

      $("<span/>").addClass("fas fa-big fa-" + file_data.icon).css("display", "block").prependTo(elem);
    }

    var col = $("<div/>").addClass("mb-3 text-center col-xl-2 col-lg-3 col-md-4 col-sm-4 col-6");
    col.attr("title", file_data.name);
    col.append(elem);

    return col;
  }

  // overrides base function
  // add button to upload media on-the-fly
  setup_header() {
    var _this = this;
    // call parent function to set title
    super.setup_header();

    // MediaUploader is optional
    if (this.media_uploader) {
      var upload_button = $("<button/>").addClass("btn btn-primary mr-2").attr("type", "button");
      upload_button.append($("<span/>").addClass("fas fa-file-upload mr-2"));
      upload_button.append(" Upload");
      upload_button.click(function() {
        _this.media_uploader.open_modal();
      });

      $(this.header + " .form-inline").prepend(upload_button);
    }
  }

  // called when an image is successfully uploaded asynchronously via the MediaUploader
  // adds the newly uploaded file to the gallery and hooks up a button
  // in the MediaUploader to add the item to the selection
  // NOTE: the newly added file will be visible, even if it does not match the current filter
  // this is _intended_ behaviour, so it is more obvious that the file was added
  on_successful_upload(new_file_info) {
    var _this = this;
    var footer = _this.media_uploader.get_footer();

    // create new single-modal-element
    var new_elem = _this.insert_single_data(new_file_info);

    // add data-* tags
    new_elem = _this.tag_data(new_elem, new_file_info);

    // hook up onclick
    new_elem.click(function() {
      _this.elem_clicked($(this));
    });

    // find category and add to category
    var cat = $(_this.body + " #cat-" + new_file_info.category);
    cat.find(".row").append(new_elem);

    // update counter
    _this.update_count_for_category(cat);

    // button to add the newly uploaded file to the selection
    var add_button = $('<button/>').attr("type", "button").addClass("btn btn-primary ml-auto").text("Add to Selection");

    add_button.click(function() {
      // "click" on element once to select it
      // done this way so stuff like allow_multiselect is honored and counters are updated
      _this.elem_clicked(new_elem);

      _this.media_uploader.close_modal();

      // calculate scroll position
      // body-offset of element - body-offset of first category = relative offset inside modal
      // adjust with half heights so that element is in the center
      var elem_offset = $(new_elem).offset().top - $(_this.body + " > div[id^=cat]:first").offset().top; - ($(_this.body).height() / 2) + ($(new_elem).height() / 2);

      $(_this.body).stop().animate({'scrollTop': elem_offset}, 900, 'swing', function() {
        // poor mans blink
        $(new_elem).fadeOut(200).fadeIn(200).fadeOut(200).fadeIn(200).fadeOut(200).fadeIn(200);
      });
    });

    footer.prepend(add_button);
  }
}