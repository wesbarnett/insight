chrome.storage.sync.get(['newSubmissionsCheckmark', 'alreadySubmittedCheckmark', 'keyupDelayValue'], function(result) {
	if (result.newSubmissionsCheckmark != undefined) {
		document.getElementById('newSubmissionsCheckmark').checked = result.newSubmissionsCheckmark;
	}
	if (result.alreadySubmittedCheckmark != undefined) {
		document.getElementById('alreadySubmittedCheckmark').checked = result.alreadySubmittedCheckmark;
	}
	if (result.keyupDelayValue != undefined) {
		document.getElementById('keyupDelayValue').value = result.keyupDelayValue;
	}
});

document.getElementById("newSubmissionsCheckmark").addEventListener('click', function() {
	document.getElementById('saved').style.display='none';
	isChecked = document.getElementById("newSubmissionsCheckmark").checked;
	chrome.storage.sync.set({newSubmissionsCheckmark: isChecked}, function() {
		document.getElementById('saved').style.display='block';
	})
});

document.getElementById("alreadySubmittedCheckmark").addEventListener('click', function() {
	document.getElementById('saved').style.display='none';
	isChecked = document.getElementById("alreadySubmittedCheckmark").checked;
	chrome.storage.sync.set({alreadySubmittedCheckmark: isChecked}, function() {
		document.getElementById('saved').style.display='block';
	})
});

document.getElementById("keyupDelayValue").addEventListener('keyup', function() {
	document.getElementById('saved').style.display='none';
	delayValue = document.getElementById("keyupDelayValue").value;
	console.log(delayValue);
	chrome.storage.sync.set({keyupDelayValue: delayValue}, function() {
		document.getElementById('saved').style.display='block';
	})
});
