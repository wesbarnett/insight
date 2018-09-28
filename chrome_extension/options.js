document.getElementById('resetButton').addEventListener('click', function() {
    document.getElementById('threshold').value = -10;
    document.getElementById('max_predictions').value = 9;
    document.getElementById('saved').style.display = "none";
    document.getElementById('oldSubs').checked = true;
    document.getElementById('newSubs').checked = true;
});

document.getElementById('threshold').addEventListener('click', function() {
    document.getElementById('saved').style.display = "none";
});

document.getElementById('oldSubs').addEventListener('click', function() {
    document.getElementById('saved').style.display = "none";
});

document.getElementById('newSubs').addEventListener('click', function() {
    document.getElementById('saved').style.display = "none";
});

document.getElementById('max_predictions').addEventListener('click', function() {
    document.getElementById('saved').style.display = "none";
});

document.getElementById('submitButton').addEventListener('click', function() {
    threshold = document.getElementById('threshold').value / 10.0
    max_per_model = document.getElementById('max_predictions').value / 3
    newSubs = document.getElementById('newSubs').checked;
    oldSubs = document.getElementById('oldSubs').checked;
    chrome.storage.sync.set({max_per_model: max_per_model, threshold: threshold, oldSubs: oldSubs, newSubs: newSubs}, function() {
        document.getElementById('saved').style.display = "block";
    });
});
