// This is for the "old" Reddit format. May have to look into the new format as well.


// Handles the click. Sends the title and text to the remote server to run prediction on
function handler() {
	var title = $('#title-field').find('textarea[name="title"]').val();
	var text = $('#text-field').find('textarea[name="text"]').val();
	$.ajax
	({
		type: "POST",
		url: "https://insight.barnett.science/api/add_message/1234",
        // TODO: remove following after done with local testing
		//url: "http://localhost:8080/api/add_message/1234",
		dataType: "json",
		data: JSON.stringify({ "title": title, "text" : text}),
		contentType: "application/json",
		success: function (result) {
            // TODO: Make this a link the user can click and then populate the "choose
            // where to post" field or add link to subscribe.
            $('#insightsuggestions').text(" ");
            for (var i = 0; i < result.length; i++) {
                $('#insightsuggestions').append('<a style="font-size: small;" href="#" class="sr-suggestion" tabindex="100">' + result[i] + '</a> ');
            }
            $('#insightlink').html('update my suggestions')
		}
	});
}

// Create a link with a specific ID that will be clicked
$('span:contains("choose where to post")').append('<p><a href="javascript:void(0);" id="insightlink">give me suggestions</a><div id="loadingDiv" class="error">loading...</div><div id="insightsuggestions"></div></p>');

$('#loadingDiv').hide();

$(document)
    // Waits for link with ID to be clicked
    .ready(function() {
        $("#insightlink").click(handler);
    })
    .ajaxStart(function () {
        $("#loadingDiv").show();
        $('#insightsuggestions').html("");
    })
    .ajaxStop(function () {
        $("#loadingDiv").hide();
    });

