// Code goes here


var global_api_url = global_host_url + "/api/v1/resources/";
var global_markdown_file_name = "";
var global_image_file_name = "";

var save_button  = "            <button style=\"margin:5px;\" onclick=\"save_markdown()\" type=\"button\" class=\"pull-right btn btn-success btn-sm\">";
save_button     += "                <span class=\"glyphicon glyphicon-save\" aria-hidden=\"true\"></span>";
save_button     += "            </button>";

function save_markdown(markdown){
  data = {};
  data.name = $('#markdown_name').text();
  data.markdown = markdown;
  console.log(data);
  $.post( global_api_url + "save_markdown", data);
}

function get_first_markdown_file(){
  first_markdown_name = "";
  $.get(global_api_url + "get_markdown_names", function(data){
    if (data.markdown_names.length >= 1){
      $('#markdown_name').html(data.markdown_names[0] + save_button);
      get_markdown_data(data.markdown_names[0]);
    }
  },null,null,false);
  return first_markdown_name;
}

function get_markdown_data(markdown_friendly_name){
  var markdown_data_url = global_api_url +
  "get_markdown?markdown_name=" +
  markdown_friendly_name;
  $.get(markdown_data_url, function(data){
    $('#comment-md').val(data);
    $('#markdown_name').html(markdown_friendly_name + save_button);
  });
}

function get_markdown_names(){
  $.get(global_api_url + "get_markdown_names", function(data){
    $('.markdown_files').html("");
    for (var i=0; i < data.markdown_names.length; i++){
      html =  "      <div class=\"file_rollover mt-5 col-lg-12\">";
      html += "          <span class=\"file_rollover\" onclick=\"get_markdown_data('"+data.markdown_names[i].trim()+"')\">" + data.markdown_names[i].trim();
      html += "        </span>";
      html += "            <button class=\"btn btn-success btn-xs pull-right\" onclick=\"get_markdown_data('"+data.markdown_names[i].trim()+"')\">Show</button> ";
      html += "            <button class=\"btn btn-danger btn-xs pull-right\" data-delete-name=\""+data.markdown_names[i].trim()+"\" onclick=\"delete_markdown_file_modal('"+data.markdown_names[i].trim()+"')\">Delete</button>";
      html += "      </div></div>";
      $('.markdown_files').append(html);
    }
  });
}

function get_images(){
  $.get(global_api_url + "get_image_filenames", function(data){
    $('.image_files').html("");
    for (var i=0; i < data.image_files.length; i++){
      short_path = data.image_files[i].trim().replaceAll(global_images_path, "");
      html =  "      <div class=\"file_rollover mt-5 col-lg-12\">";
      html += "          <span class=\"file_rollover\">" + short_path;
      html += "        </span>";
      html += "            <a href=\""+data.image_files[i].trim()+"\" target=\"_blank\" class=\"btn btn-success btn-xs pull-right\">Show</a> ";
      html += "            <button class=\"btn btn-danger btn-xs pull-right\" ";
      html += "                   data-delete-name=\""+data.image_files[i].trim()+"\" ";
      html += "                   onclick=\"delete_image_file_modal('"+data.image_files[i].trim()+"')\">Delete</button>";
      html += "      </div></div>";
      $('.image_files').append(html);
    }
  });
}


function delete_markdown_file_modal(markdown_name){
  global_markdown_file_name = markdown_name;
  $('#deleteMarkdownModal').modal('toggle');
}

function delete_image_file_modal(image_filename){
  global_image_file_name = image_filename;
  $('#deleteImageModal').modal('toggle');
}

function delete_markdown_file() {
  $('#deleteMarkdownModal').modal('toggle');
  if (global_markdown_file_name > ""){
    $.get(global_api_url +
      "delete_markdown" +
      "?markdown_name=" +
      global_markdown_file_name, function(data){
        if (data){
          if(data === "File deleted successfully."){
            get_markdown_names();
          }
        }
        else{
          alert("Something went wrong deleting the markdown file");
        }
      });
    global_markdown_file_name = "";
  }
}

function delete_image_file() {
  $('#deleteImageModal').modal('toggle');
  if (global_image_file_name > ""){
    encoded_image_filename = encodeURIComponent(global_image_file_name);
    $.get(global_api_url +
      "delete_image" +
      "?image_file_path=" +
      encoded_image_filename, function(data){
        console.log(data);
        if (data){
          get_images();
        }
        else{
          alert("Something went wrong deleting the image file");
        }
      });
    global_image_file_name = "";
  }
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
// ## Doc Ready
$(function() {
  var $previewContainer = $('#comment-md-preview-container');
  $previewContainer.hide();

  $('#deleteMarkdownModal').on('show.bs.modal', function (e) {
    $("#curCarModal").modal('toggle', $("#curCarSelect"));

  });
  get_markdown_names();
  get_images();
  get_first_markdown_file();

  var $md = $("#comment-md").markdown({
    autofocus: false,
    savable:true,
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
    onSave: function(e) {
      save_markdown(e.getContent())
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