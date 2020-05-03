
/*
 * Archivar's own MediaUploader class, which loads and handles the MediaCreateForm asynchronously.
 * Provides a hook that is called when the upload is successful, so the result can be used without a page reload.
 */
class MediaUploader {
  /*
   * url: where to load the form from / send the form to
   * opts:
   *    - onSuccess: "value",   function to be called when a file as successfully uploaded
   *                            takes a single parameter, which is an object containing information about the uploaded file
   *    - parent: parent-element for the modal
   */
  constructor(url, opts) {
    this.upload_url = url;
    this.parent = "body"
    this.modal_id = "media-ajax-modal"

    // set opts
    if (opts) {
      if (opts.onSuccess)
        this.success_fkt = opts.onSuccess

      if (opts.parent)
        this.parent = opts.parent
    }

    // add modal to DOM
    this.insert_modal()
  }

  // insert modal into DOM inside of this.parent
  // only done once (even if multiple instances of MediaUploader exist)
  insert_modal() {
    if (!$("#media-ajax-modal").length) {
      $(this.parent).append('<div class="modal" id="' + this.modal_id + '" data-backdrop="static"> \
          <div class="modal-dialog"> \
              <div class="modal-content"> \
                  <div class="modal-header"> \
                      <h5 class="modal-title">Upload new File</h5> \
                      <button type="button" class="close" data-dismiss="modal"> \
                          <span class="fas fa-times"></span> \
                      </button> \
                  </div> \
                  <div class="modal-body"></div> \
                  <div class="modal-footer"> \
                  </div> \
              </div> \
          </div> \
      </div>');
    }
  }

  // load the ajax form asynchronously and hook up the ajax-form-handling
  open_modal() {
    var _this = this;
    var modal_id = "#" + _this.modal_id;

    // load the form into the modal
    $(modal_id + " .modal-body").load(_this.upload_url, function() {

      // override submit-function of the form
      $(modal_id + ' form').submit(function (e) {
        e.preventDefault();

        $.ajax({
          type: "POST",
          url: _this.upload_url,
          processData: false, //< must be false for FormData
          contentType: false, //< must be false for FormData
          data: new FormData(this), //< serialize Form (includes the file-data)
          dataType: 'json',
          beforeSend: function() {
            // disable the submit button after it was pressed, so it is not clicked twice
            $(modal_id + " #fake-submit").attr("disabled", "disabled");
          },
          success: function(resp) { //< called when the request completes successfully
            // response contains html to display inside modal
            $(modal_id + " .modal-body").html(resp.data.html);

            // check if file was uploaded correctly
            if (resp.data.success == true) {
              // hide submit-button
              $(modal_id + " #fake-submit").hide();

              // if a success-fkt was give, execute it with the information about the uploaded file
              if (_this.success_fkt) {
                _this.success_fkt(resp.data.media_info)
              }
            } else {
              // success = false -> show form validation hints
              $(modal_id + " .modal-body .invalid-feedback").show();
            }
          },
          error: function(resp, textStatus, errorThrown) { //< called when the server reports an error
            switch(resp.status) {
                case 413: //< special case for HTTP 413
                  $(modal_id + " .modal-body").html($("<p/>").addClass("alert alert-danger").text("The image you wanted to upload was too large."));
                  break;
                default:
                  $(modal_id + " .modal-body").html($("<p/>").addClass("alert alert-danger").text("A server-side error occured. If this problem consists, please contact the administrator. (Hints: " + textStatus + ", " + errorThrown + ")"));
            }

            // spawn a retry-button which reloads the form
            var retry_button = $("<button/>").attr("type", "butto").addClass("btn btn-primary mr-auto").text("Upload new File");
            retry_button.click(function() {
                recurse.open_modal();
            });

            $(modal_id + " #fake-submit").replaceWith(retry_button);
          }
        });
      });

      // spawn modal-footer
      $(modal_id + " .modal-footer").html('<button type="button" class="btn btn-success mr-auto" id="fake-submit">Upload File</button> \
                                           <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>');

      // hook up fake-submit to real submit button
      $(modal_id + ' .modal-footer #fake-submit').click(function() {
        $(modal_id + " #submit").click();
      });

      $(modal_id).modal("show");
    });
  }

  // close the modal
  close_modal() {
    $("#" + this.modal_id).modal("hide");
  }

  // get modal header
  get_header() {
    return $("#" + this.modal_id + " .modal-header");
  }

  // get modal body
  get_body() {
    return $("#" + this.modal_id + " .modal-body");
  }

  // get modal footer
  get_footer() {
    return $("#" + this.modal_id + " .modal-footer");
  }
}