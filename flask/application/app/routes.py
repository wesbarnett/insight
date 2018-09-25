from app import app
from flask import Flask, request, jsonify, render_template, url_for
from joblib import load
import nlp_scripts
import praw
import sklearn
from sklearn.feature_extraction.text import HashingVectorizer

wwwdir = "/var/www/apache-flask/application/app/"

with open(wwwdir + 'config.in') as f:
    client_id=f.readline().strip('\n')
    client_secret=f.readline().strip('\n')
    refresh_token=f.readline().strip('\n')
    user_agent=f.readline().strip('\n')

reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     refresh_token=refresh_token,
                     user_agent=user_agent)

print(reddit.user.me())
vectorizer = HashingVectorizer(
    decode_error="ignore", analyzer=nlp_scripts.stemmed_words, n_features=2 ** 18,
    norm="l1", alternate_sign=False
)

clf = [load(wwwdir + 'MODELS/sgd_svm_large.gz'),
    load(wwwdir + 'MODELS/sgd_svm_med.gz'),
    load(wwwdir + 'MODELS/sgd_svm_small.gz')]

@app.route("/")
@app.route("/index")
def index():
    """
    This route is the main landing page which will direct users to install the Chrome
    extension.
    """
    page = {}
    page['title'] = 'Subreddits with Content Like This'
    return render_template("index.html", page=page)

@app.route("/api/add_message/<uuid>", methods=["GET", "POST"])
def add_message(uuid):
    """
    This route will be accessed remotely from the Chrome extension. It takes the user
    input (which is the Reddit submission's title and text) and returns the top 3
    predicted subreddits for each model. Then it returns the results back to the
    extension so it can display them.
    """
    content = request.json
    print(content)
    title = content["title"]
    text = content["text"]
    X = title + " " + text
    X = vectorizer.transform([X])

    selected_predictions = []
    for i in clf:
        with sklearn.config_context(assume_finite=True):
            argsorted_dec = i.decision_function(X).argsort()[0][::-1]
            sorted_classes = i.classes_[argsorted_dec]
        selected_predictions += list(sorted_classes[:3])

    return jsonify(selected_predictions)

@app.route("/api/already_posted/<uuid>", methods=["GET", "POST"])
def already_posted(uuid):
    content = request.json
    print(content)

    submission = praw.models.Submission(reddit, url=content["url"])

    title = submission.title
    text = submission.selftext
    subreddit = submission.subreddit
    X = title + " " + text
    X = vectorizer.transform([X])

    selected_predictions = []
    for i in clf:
        with sklearn.config_context(assume_finite=True):
            argsorted_dec = i.decision_function(X).argsort()[0][::-1]
            sorted_classes = i.classes_[argsorted_dec]
        selected_predictions += list(sorted_classes[:3])

    # Remove prediction if it is the same subreddit you are in
    # TODO?
    #if subreddit in selected_predictions:
    #    selected_predictions.remove(subreddit)

    return jsonify(selected_predictions)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
