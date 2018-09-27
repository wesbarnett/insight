function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

chrome.storage.sync.clear();
chrome.runtime.onInstalled.addListener(function() {
    myuuid = uuidv4()
    chrome.storage.sync.set({uuid: myuuid, max_per_model: 3, threshold: -1}, function() {
        console.log("uuid = " + myuuid);
    });
});
