// This is for the "old" Reddit format. May have to look into the new format as well.

// Handles the key press event. Sends the title and text to the remote server to run prediction on
function handler() {
	var title = $('#title-field').find('textarea[name="title"]').val();
	var text = $('#text-field').find('textarea[name="text"]').val();
    if ((title) || (text) ){
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
                myhtml =  '<p style="font-size: x-small;">subscribers &gt; 130,000</p><p>';
                for (var i = 0; i < 3; i++) {
                    myhtml += '<a style="font-size: medium;" target="_blank" href="https://www.reddit.com/r/' + result[i] + '/submit?selftext=true&title=' + title + '&text=' + text +'" class="sr-suggestion" tabindex="100">' + result[i] + '</a>';
                    if (i != 2) {
                        myhtml += ' &middot; '
                    }
                }
                myhtml += '</p><br><p style="font-size: x-small;">130,000 &gt; subscribers &gt; 55,000</p><p>';
                for (var i = 3; i < 6; i++) {
                    myhtml += '<a style="font-size: medium;" target="_blank" href="https://www.reddit.com/r/' + result[i] + '/submit?selftext=true&title=' + title + '&text=' + text +'" class="sr-suggestion" tabindex="100">' + result[i] + '</a>';
                    if (i != 5) {
                        myhtml += ' &middot; '
                    }
                }
                myhtml += '</p><br><p style="font-size: x-small;">55,000 &gt; subscribers &gt; 33,000</p><p>';
                for (var i = 6; i < result.length; i++) {
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

var string = window.location.href,
substring0 = "submit";
substring1 = "comments";

// NEW POSTS -----------------------------------------
if (string.indexOf(substring0) !== -1) {

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

    $('#title-field').find('textarea[name="title"]').bindWithDelay("keyup", handler, 100);
    $('#text-field').find('textarea[name="text"]').bindWithDelay("keyup", handler, 100);

// ALREADY SUBMITTED ------------------------------------------------
} else if (string.indexOf(substring1) !== -1) {

    $('.flat-list:eq(3)').parent().append('<div class="reddit-infobar"><div style="font-size: large;" id="insightsuggestions"><b>communities with content like this</b><span class="error">&nbsp;&nbsp;&nbsp;loading...</span></div></div>');
    $.ajax
    ({
        type: "POST",
        url: "https://insight.barnett.science/api/already_posted/1234",
        dataType: "json",
        data: JSON.stringify({ "url": window.location.href}),
        contentType: "application/json",
        success: function (result) {
            if (result != "") {
                myhtml = '<div style="font-size: large; line-height: 1.2em"><b>communities with content like this</b></div>';
                myhtml += '<p style="font-size: x-small;">subscribers &gt; 130,000</p><p>';
                for (var i = 0; i < 3; i++) {
                    myhtml += '<a target="_blank" style="font-size: medium;" href="https://reddit.com/r/' + result[i] + '">' + result[i] + '</a> ';
                    if (i != 2) {
                        myhtml += ' &middot; '
                    }
                }
                myhtml += '</p><br><p style="font-size: x-small;">130,000 &gt; subscribers &gt; 55,000</p><p>';
                for (var i = 3; i < 6; i++) {
                    myhtml += '<a target="_blank" style="font-size: medium;" href="https://reddit.com/r/' + result[i] + '">' + result[i] + '</a> ';
                    if (i != 5) {
                        myhtml += ' &middot; '
                    }
                }
                myhtml += '</p><br><p style="font-size: x-small;">55,000 &gt; subscribers &gt; 33,000</p><p>';
                for (var i = 6; i < result.length; i++) {
                    myhtml += '<a target="_blank" style="font-size: medium;" href="https://reddit.com/r/' + result[i] + '">' + result[i] + '</a> ';
                    if (i != result.length-1) {
                        myhtml += ' &middot; '
                    }
                }
                myhtml += '</p>';
                $('#insightsuggestions').html(myhtml);
            }
        },
        error: function(xhr, status, error) {
            $('#insightsuggestions').html('<p class="error">error loading communities with similar content</p>');
        }
    });
}
