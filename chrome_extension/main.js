// This is for the "old" Reddit format. May have to look into the new format as well.

// Waits for link with ID to be clicked
$(document).ready(function() {
  $("#insightlink").click(handler);
});

// Handles the click. Sends the title and text to the remote server to run prediction on
function handler() {
	var title = $('#title-field').find('textarea[name="title"]').val();
	var text = $('#text-field').find('textarea[name="text"]').val();
	$.ajax
	({
		type: "POST",
		url: "http://localhost:8080/api/add_message/1234",
		dataType: "json",
		async: false,
		data: JSON.stringify({ "title": title, "text" : text}),
		contentType: "application/json",
		success: function () {
			alert(title); 
		}
	});
}

// Create a link with a specific ID that will be clicked
$('#suggested-reddits').append('<h1><a href="javascript:void(0);" id="insightlink">Give me suggestions</a></h1>');
