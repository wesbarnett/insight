// This is for the "old" Reddit format. May have to look into the new format as well.

// Handles the key press event. Sends the title and text to the remote server to run prediction on
function handler() {
	var title = $('#title-field').find('textarea[name="title"]').val();
	var text = $('#text-field').find('textarea[name="text"]').val();
	$.ajax
	({
		type: "POST",
		url: "https://insight.barnett.science/api/add_message/1234",
		dataType: "json",
		data: JSON.stringify({ "title": title, "text" : text}),
		contentType: "application/json",
		success: function (result) {
            // TODO: Make this a link the user can click and then populate the "choose
            // where to post" field or add link to subscribe.
            $('#insightsuggestions').html(" ");
            for (var i = 0; i < result.length; i++) {
                $('#insightsuggestions').append('<a style="font-size: small;" href="#" class="sr-suggestion" tabindex="100">' + result[i] + '</a> ');
            }
            $('#insightlink').html('');
		},
        error: function(xhr, status, error) {
            $('#insightsuggestions').html('<p class="error">error loading communities with similar content</p>');
        }
	});
}

chrome.storage.sync.clear();
chrome.storage.sync.get(['newSubmissionsCheckmark', 'alreadySubmittedCheckmark', 'keyupDelayValue'], function(result) {

    doNewSubmissions = result.newSubmissionsCheckmark;
    doOldSubmissions = result.alreadySubmittedCheckmark;
    keyupDelay = result.keyupDelayValue;

    // Defaults
    if (doNewSubmissions == undefined) { 
        doNewSubmissions = true; 
    }
    if (doOldSubmissions == undefined) { 
        doOldSubmissions = true; 
    }
    if (keyupDelay == undefined) { 
        keyupDelay = 100;
    }

    var string = window.location.href,
    substring0 = "submit";
    substring1 = "comments";
    if (string.indexOf(substring0) !== -1 && doNewSubmissions) {

        // Currently only works on subreddits that take self text posts
        $('.bottom-area:first').parent().append('<div style="font-size: large;">communities with content like this<span id="loadingDiv" class="error">&nbsp;&nbsp;&nbsp;loading...</span></div><div id="insightsuggestions">start typing above!</div>');

        $('#loadingDiv').hide();

        $(document)
            .ajaxStart(function () {
                $("#loadingDiv").show();
            })
            .ajaxStop(function () {
                $("#loadingDiv").hide();
            });

        $('#title-field').find('textarea[name="title"]').bindWithDelay("keyup", handler, keyupDelay);
        $('#text-field').find('textarea[name="text"]').bindWithDelay("keyup", handler, keyupDelay);

    } else if (string.indexOf(substring1) !== -1 && doOldSubmissions) {

        $('.flat-list:eq(3)').append('<div style="font-size: large;" id="insightsuggestions">communities with content like this<span class="error">&nbsp;&nbsp;&nbsp;loading...</span></div>');
        $.ajax
        ({
            type: "POST",
            url: "https://insight.barnett.science/api/already_posted/1234",
            dataType: "json",
            data: JSON.stringify({ "url": window.location.href}),
            contentType: "application/json",
            success: function (result) {
                if (result != "") {
                    $('#insightsuggestions').html('<div style="font-size: large;">communities with content like this</div>');
                    for (var i = 0; i < result.length; i++) {
                        $('#insightsuggestions').append('<a style="font-size: small;" href="https://old.reddit.com/r/' + result[i] + '">' + result[i] + '</a> ');
                    }
                }
            },
            error: function(xhr, status, error) {
                $('#insightsuggestions').html('<p class="error">error loading communities with similar content</p>');
            }
        });
    }

});
