from app import app
from flask import Flask, request, jsonify, render_template
from joblib import load
import nlp_scripts
from sklearn.feature_extraction.text import HashingVectorizer

# TODO:Right now suggests three subreddits. Should we make this more dynamic (based on some
# threshold?

vectorizer = HashingVectorizer(
    decode_error="ignore", analyzer=nlp_scripts.stemmed_words, n_features=2 ** 18,
    alternate_sign=False
)

#wwwdir = "/var/www/apache-flask/application"
# TODO: Remove when done testing locally
wwwdir = '/home/wes/Documents/data-science/insight/PROJECT/flask/application'
clf = load(wwwdir + "/sgd.gz")

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", page="index")

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

    argsorted_probs = clf.predict_proba(X).argsort()[0][::-1]
    sorted_classes = clf.classes_[argsorted_probs]
    selected_predictions = list(sorted_classes[:3])

    return jsonify(selected_predictions)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
