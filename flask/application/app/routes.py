from app import app
from flask import Flask, request, jsonify, render_template, url_for
from joblib import load
import nlp_scripts
import praw
from sklearn.feature_extraction.text import HashingVectorizer

# TODO:Right now suggests three subreddits. Should we make this more dynamic (based on some
# threshold?

wwwdir = "/var/www/apache-flask/application/app/"
#wwwdir = '/home/wes/Documents/data-science/insight/PROJECT/flask/application/'

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

#clf = []
#clf.append(load(wwwdir + 'MODELS_L1_NORM/sgd_svm_large.gz'))
#clf.append(load(wwwdir + 'MODELS_L1_NORM/sgd_svm_large.gz'))
#clf.append(load(wwwdir + 'MODELS_L1_NORM/sgd_svm_med.gz'))
clf = load(wwwdir + 'MODELS/sgd_log_small.gz')

#clf = load(wwwdir + "sgd.gz")

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
    input (which is the Reddit submission's title and text and runs a prediction on it
    based on our previously trained model. Then it returns the results back to the
    extension so it can display them.
    """
    content = request.json
    print(content)
    title = content["title"]
    text = content["text"]
    X = title + " " + text
    X = vectorizer.transform([X])

    # Logistic Regression; TODO: remove
    argsorted_probs = clf.predict_proba(X).argsort()[0][::-1]
    sorted_classes = clf.classes_[argsorted_probs]
    selected_predictions = list(sorted_classes[:3])

    # SVM; TODO: use decision function to rank multiple per model
    #selected_predctions = []
    #for i in clf:
    #    selected_predctions.append(i.predict(X))

    return jsonify(selected_predictions)

@app.route("/api/already_posted/<uuid>", methods=["GET", "POST"])
def already_posted(uuid):
    content = request.json
    print(content)

    if "/comments/" in content["url"]:

        submission = praw.models.Submission(reddit, url=content["url"])

        title = submission.title
        text = submission.selftext
        X = title + " " + text
        X = vectorizer.transform([X])

        # Logistic Regression; TODO: remove
        argsorted_probs = clf.predict_proba(X).argsort()[0][::-1]
        sorted_classes = clf.classes_[argsorted_probs]
        selected_predictions = list(sorted_classes[:3])

        # SVM; TODO: use decision function to rank multiple per model
        #selected_predctions = []
        #for i in clf:
        #    selected_predctions.append(i.predict(X))

        return jsonify(selected_predictions)

    # TODO: handle this better
    else:

        return ""

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
