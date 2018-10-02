// This is for the "old" Reddit format. May have to look into the new format as well.

// Handles the key press event. Sends the title and text to the remote server to run prediction on
function handler() {
	var title = $('#title-field').find('textarea[name="title"]').val();
	var text = $('#text-field').find('textarea[name="text"]').val();
    if ((title) || (text) ){
        $.ajax
        ({
            type: "POST",
            url: "https://insight.barnett.science/api/add_message/" + uuid,
            dataType: "json",
            data: JSON.stringify({ "title": title, "text" : text, "max_per_model": max_per_model, "threshold": threshold}),
            contentType: "application/json",
            success: function (result) {
                myhtml = ""
                for (var i = 0; i < result.length; i++) {
                    myhtml += '<a style="font-size: medium;" target="_blank" href="https://www.reddit.com/r/' + result[i] + '/submit?selftext=true&title=' + title + '&text=' + text +'" class="sr-suggestion" tabindex="100">' + result[i] + '</a>';
                    if (i != result.length-1) {
                        myhtml += ' &middot; '
                    }
                }
                myhtml += '</p>';
                $('#insightsuggestions').html(myhtml)
                $('#insightlink').html('');
            },
            error: function(xhr, status, error) {
                $('#insightsuggestions').html('<p class="error">error loading communities with similar content</p>');
            }
        });
    }
    else {
        $('#insightsuggestions').html('start typing above!');
    }
}

var string = window.location.href;
substring0 = "submit";
substring1 = "comments";

chrome.storage.sync.get(['uuid', 'max_per_model', 'threshold', 'oldSubs', 'newSubs'], function(result) {

	uuid = result.uuid;
    max_per_model = result.max_per_model;
    threshold = result.threshold;
    oldSubs = result.oldSubs;
    newSubs = result.newSubs;

	// NEW POSTS -----------------------------------------
	if ((string.indexOf(substring0) !== -1) && newSubs) {

		// Currently only works on subreddits that take self text posts
		$('.bottom-area:first').parent().append('<div class="reddit-infobar"><div style="font-size: large; font-weight: bold;">communities with content like this<span id="loadingDiv" class="error">&nbsp;&nbsp;&nbsp;loading...</span></div><div id="insightsuggestions">start typing above!</div></div>');

		$('#loadingDiv').hide();

		$(document)
			.ajaxStart(function () {
				$("#loadingDiv").show();
			})
			.ajaxStop(function () {
				$("#loadingDiv").hide();
			});

		$('#title-field').find('textarea[name="title"]').bindWithDelay("keyup", handler, 150);
		$('#text-field').find('textarea[name="text"]').bindWithDelay("keyup", handler, 150);
        handler();

	// ALREADY SUBMITTED ------------------------------------------------
	} else if ((string.indexOf(substring1) !== -1) && oldSubs) {

		$('.flat-list:eq(3)').parent().append('<br><div class="reddit-infobar" id="insightsuggestionsbar"><div style="font-size: large;" id="insightsuggestions"><b>other communities with content like this<span class="error">&nbsp;&nbsp;&nbsp;loading...</span></div></div>');
		$.ajax
		({
			type: "POST",
			url: "https://insight.barnett.science/api/already_posted/" + uuid,
			dataType: "json",
			data: JSON.stringify({ "url": window.location.href, "max_per_model": max_per_model, "threshold": threshold}),
			contentType: "application/json",
			success: function (result) {
				if (result.length > 0) {
					myhtml = '<div style="font-size: large; line-height: 1.2em"><b>other communities with content like this</b></div>';
					for (var i = 0; i < result.length; i++) {
						myhtml += '<a target="_blank" style="font-size: medium;" href="https://reddit.com/r/' + result[i] + '">' + result[i] + '</a> ';
						if (i != result.length-1) {
							myhtml += ' &middot; '
						}
					}
					myhtml += '</p>';
					$('#insightsuggestions').html(myhtml);
				}
				else {
					$('#insightsuggestionsbar').remove()
				}
			},
			error: function(xhr, status, error) {
				$('#insightsuggestions').html('<p class="error">error loading communities with similar content</p>');
			}
		});
	}

});
