// Code goes here

var global_api_url = global_host_url + "/api/v1/resources/"
function get_markdown_data(markdown_friendly_name){
  var markdown_data_url = global_api_url +
                          "get_markdown?markdown_name=" +
                          markdown_friendly_name;

}
function get_markdown_names(){
  $.get(global_api_url + "get_markdown_names", function(data){
    $('.markdown_files').html("");
    for (var i=0; i < data.markdown_names.length; i++){
      $('.markdown_files').append("<div onclick=\"get_markdown_data('"+data.markdown_names[i].trim()+"');\">" + data.markdown_names[i] + "</div>");
    }
  });
}

function create_new_markdown_file() {
  var new_markdown_filename = encodeURIComponent($('#new_markdown_filename').val());
  if (!new_markdown_filename.endsWith(".md")){
    alert("Please ensure the filename ends in '.md'");
  }
  var file_created = null;
  $.get(global_api_url +
        "create_markdown_file" +
        "?markdown_filename=" +
        new_markdown_filename, function(data){
          console.log(data);
          if (data){
            if(data.success === "File successfully created."){
              markdown_friendly_name = new_markdown_filename.replaceAll(".md", "")
              get_markdown_names();
              get_markdown_data(markdown_friendly_name);
            }
          }
          else{
            alert("Something went wrong creating the new markdown file");
            alert(file_created);
          }
        });
}
$(function() {
  var $previewContainer = $('#comment-md-preview-container');
  $previewContainer.hide();


  get_markdown_data('hello');

  get_markdown_names();



  var $md = $("#comment-md").markdown({
    autofocus: false,
    height: 270,
    iconlibrary: 'fa',
    onShow: function(e) {
      //e.hideButtons('cmdPreview');
      e.change(e);
    },
    onChange: function(e) {
      var content = e.parseContent();
      if (content === '') $previewContainer.hide();
      else $previewContainer.show()
                            .find('#comment-md-preview')
                            .html(content)
                            .find('table')
                            .addClass('table table-bordered table-striped table-hover');
    },
    footer: function(e) {
      return '\
					<span class="text-muted">\
						<span data-md-footer-message="err">\
						</span>\
						<span data-md-footer-message="default">\
							Add images by dragging & dropping or \
							<a class="btn-input">\
								selecting them\
								<input type="file" multiple="" id="comment-images" />\
							</a>\
						</span>\
						<span data-md-footer-message="loading">\
							Uploading your images...\
						</span>\
					</span>';
    }
  });

  var $mdEditor = $('.md-editor'),msgs = {};

  $mdEditor.find('[data-md-footer-message]').each(function() {
    msgs[$(this).data('md-footer-message')] = $(this).hide();
  });

  msgs.default.show();

  // upload url
  upload_url = window.location.origin + "/api/v1/resources/upload_image";

  $mdEditor.filedrop({
    binded_input: $('#comment-images'),
    url: upload_url,
    fallbackClick: false,
    beforeSend: function(file, i, done) {
      msgs.default.hide();
      msgs.err.hide();
      msgs.loading.show();
      done();
    },
    //maxfilesize: 15,
    error: function(err, file) {
      switch (err) {
        case 'BrowserNotSupported':
          //alert('browser does not support HTML5 drag and drop')
          alert("error message: " + err)
          break;
        case 'FileExtensionNotAllowed':
          // The file extension is not in the specified list 'allowedfileextensions'
          break;
        default:
          break;
      }
      var filename = typeof file !== 'undefined' ? file.name : '';
      msgs.loading.hide();
      msgs.err.show().html('<span class="text-danger"><i class="fa fa-times"></i> Error uploading ' + filename + ' - ' + err + '</span><br />');
    },
    dragOver: function() {
      $(this).addClass('active');
    },
    dragLeave: function() {
      $(this).removeClass('active');
    },
    progressUpdated: function(i, file, progress) {
      msgs.loading.html('<i class="fa fa-refresh fa-spin"></i> Uploading <span class="text-info">' + file.name + '</span>... ' + progress + '%');
    },
    afterAll: function() {
      msgs.default.show();
      msgs.loading.hide();
      msgs.err.hide();
    },
    uploadFinished: function(i, file, response, time) {
      $md.val($md.val() + "![" + file.name + "](" + global_image_path + file.name + ")\n").trigger('change');
      // response is the data you got back from server in JSON format.
    }
  });
})