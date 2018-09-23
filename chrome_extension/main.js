// This is for the "old" Reddit format. May have to look into the new format as well.

/*
bindWithDelay jQuery plugin
Author: Brian Grinstead
MIT license: http://www.opensource.org/licenses/mit-license.php
http://github.com/bgrins/bindWithDelay
http://briangrinstead.com/files/bindWithDelay
Usage:
    See http://api.jquery.com/bind/
    .bindWithDelay( eventType, [ eventData ], handler(eventObject), timeout, throttle )
Examples:
    $("#foo").bindWithDelay("click", function(e) { }, 100);
    $(window).bindWithDelay("resize", { optional: "eventData" }, callback, 1000);
    $(window).bindWithDelay("resize", callback, 1000, true);
*/

(function($) {

$.fn.bindWithDelay = function( type, data, fn, timeout, throttle ) {

    if ( $.isFunction( data ) ) {
        throttle = timeout;
        timeout = fn;
        fn = data;
        data = undefined;
    }

    // Allow delayed function to be removed with fn in unbind function
    fn.guid = fn.guid || ($.guid && $.guid++);

    // Bind each separately so that each element has its own delay
    return this.each(function() {

        var wait = null;

        function cb() {
            var e = $.extend(true, { }, arguments[0]);
            var ctx = this;
            var throttler = function() {
                wait = null;
                fn.apply(ctx, [e]);
            };

            if (!throttle) { clearTimeout(wait); wait = null; }
            if (!wait) { wait = setTimeout(throttler, timeout); }
        }

        cb.guid = fn.guid;

        $(this).bind(type, data, cb);
    });
};

})(jQuery);

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

$('#title-field').find('textarea[name="title"]').bindWithDelay("keydown", handler, 100);
$('#text-field').find('textarea[name="text"]').bindWithDelay("keydown", handler, 100);

// For submissions pages
$('.entry:eq(0)').append('<div id="insightsuggestions" style="font-size: large;">loading...</div>');

//  $.ajax
//  ({
//      type: "POST",
//      url: "https://insight.barnett.science/api/already_posted/1234",
//      // TODO: remove following after done with local testing
//      //url: "http://localhost:8080/api/already_posted/1234",
//      dataType: "json",
//      data: JSON.stringify({ "url": window.location.href}),
//      contentType: "application/json",
//      success: function (result) {
//          if (result != "") {
//              // TODO: Make this a link the user can click and then populate the "choose
//              // where to post" field or add link to subscribe.
//              $('#insightsuggestions').html('<h3>communities with similar content:</h3>');
//              for (var i = 0; i < result.length; i++) {
//                  $('#insightsuggestions').append('<a style="font-size: large;" href="https://old.reddit.com/r/' + result[i] + '">' + result[i] + '</a> ');
//              }
//          }
//      },
//      error: function(xhr, status, error) {
//          $('#insightsuggestions').html('<p class="error">error loading communities with similar content</p>');
//      }
//  });
