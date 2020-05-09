
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
                <a href="#" id="deselect-hidden">hidden</a> \
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

      // setup filter form
      $(modal_id + " .filter-input").on("keyup", function() {
        var value = $(this).val().toLowerCase();

        $(modal_id + " .sidebar-element").filter(function() {
          // matches() is defined in the derived class
          $(this).toggle(_this.matches($(this), value));
        });

        // update category counters after filtering
        $(modal_id + " .sidebar-category").each(function() {
          _this.update_count_for_category(this);
        });

        // update selected-count after filtering
        _this.update_active_count();
      });

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
        var cat_container = $("<div/>").addClass("m-2 sidebar-category").attr("id", "cat-" + category_data.id).append($("<h5/>").text(category_data.name).append($("<span/>").addClass("cat-count").text(" (0)"))).appendTo($(_this.body));

        // insert data into container
        _this.insert_data(resp.data, cat_container);

        // display element count for this category
        _this.update_count_for_category(cat_container);

        // hook up onclick-event for elements
        $(cat_container).find(".sidebar-element").click(function() {
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
      single_data.addClass("sidebar-element");

      // copy every member of the element into data-* attributes for usage outside
      for (var key in elem) {
        single_data.attr("data-" + key, elem[key]);
      }

      row.append(single_data);
    });

    parent.append(row);
  }

  // update how many (visible) elements are displayed in a category
  update_count_for_category(category) {
    var count = $(category).find(".sidebar-element").filter(function() {
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
    var full_count = this.get_active_elements().length;
    var count_str = full_count;

    var hidden = $(this.body).find(".sidebar-element.active").filter(function() {
        return $(this).css("display") === 'none';
    }).length;

    if (hidden > 0) {
      count_str += " (" + hidden + " hidden)";
    }

    $(this.footer).find(".active-elem-count").text(count_str);

    // disable / enable footer buttons if there are selected elements
    if (full_count > 0) {
      $(this.footer).find(".footer-btn").each(function() {
        $(this).removeClass("disabled").removeAttr("disabled");
      });
    } else {
      $(this.footer).find(".footer-btn").addClass("disabled").attr("disabled", "disabled");
    }
  }

  // get all currently selected elements
  get_active_elements() {
    return $(this.body).find(".sidebar-element.active");
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

  // set heading
  setup_header() {
    $(this.header + " h5").text(this.title);
  }

  // display and hook up footer buttons
  setup_footer() {
    var _this = this;

    this.footer_info.forEach(function(foo) {
        // buttons spawn in a disabled state
        $(foo.button).addClass("footer-btn disabled").attr("disabled", "disabled");

        // fire this buttons function when its clicked
        $(foo.button).click(function() {
            foo.func(_this.get_active_elements());
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
      elem = $("<p/>").text(file_data.name).addClass("mx-auto figure-caption text-center text-truncate mb-0");

      var icon = "file-alt";

      if (file_data["file-ext"] == "pdf") {
        icon = "file-pdf";
      }

      if (["rar", "zip", "7z", "tar", "gz", "bz2", "xz"].indexOf(file_data["file-ext"]) != -1) {
        icon = "file-archive";
      }

      $("<span/>").addClass("fas fa-" + icon).css("font-size", "48px").css("display", "block").prependTo(elem);
    }

    var col = $("<div/>").addClass("mb-3 text-center col-xl-2 col-lg-3 col-md-4 col-sm-4 col-6");
    col.attr("title", file_data.name);
    col.append(elem);

    return col;
  }
}