chrome.storage.sync.get(['newSubmissionsCheckmark', 'alreadySubmittedCheckmark'], function(result) {
	document.getElementById('newSubmissionsCheckmark').checked = result.newSubmissionsCheckmark;
	document.getElementById('alreadySubmittedCheckmark').checked = result.alreadySubmittedCheckmark;
});

document.getElementById("newSubmissionsCheckmark").addEventListener('click', function() {
	isChecked = document.getElementById("newSubmissionsCheckmark").checked;
	chrome.storage.sync.set({newSubmissionsCheckmark: isChecked}, function() {
	})
});

document.getElementById("alreadySubmittedCheckmark").addEventListener('click', function() {
	isChecked = document.getElementById("alreadySubmittedCheckmark").checked;
	chrome.storage.sync.set({alreadySubmittedCheckmark: isChecked}, function() {
	})
});
