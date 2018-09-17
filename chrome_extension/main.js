// This is for the "old" Reddit format. May have to look into the new format as well.

// TODO: randomly select subreddits from list and suggest them

// Field where user inputs subreddit name
//$('#sr-autocomplete')

// https://www.tutorialrepublic.com/faq/auto-update-div-content-while-typing-in-textarea-using-jquery.php
$(document).ready(function(){

    // When a user is typing in the title
	$('#title-field').find('textarea[name="title"]').keyup(function(){
    	// Getting the current value of textarea
        var currentText = $(this).val();

        // TODO: Get value of text area as well
        
        // TODO: Send the text to our server and run the model on it, and return
        // suggested subreddits
        suggestedSubreddits = "foo bar"

        // Setting the Div content
		$('#suggested-reddits').text('<h3>suggested subreddits</h3>' + suggestedSubreddits)
    });

    // When a user is typing in the text
	$('#text-field').find('textarea[name="text"]').keyup(function(){
    	// Getting the current value of textarea
        var currentText = $(this).val();

        // TODO: Get value of title area as well
        
        // TODO: Send the text to our server and run the model on it, and return
        // suggested subreddits
        suggestedSubreddits = "foo bar"
        
		$('#suggested-reddits').text('<h3>suggested subreddits</h3>' + suggestedSubreddits)
    });

});
