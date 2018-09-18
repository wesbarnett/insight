from app import app
from flask import Flask, request, jsonify
from joblib import load

# TODO:Right now suggests three subreddits. Should we make this more dynamic (based on some
# threshold?

@app.route('/')
@app.route('/index')
def index():
    return "It works!\n"

@app.route('/api/add_message/<uuid>', methods=['GET', 'POST'])
def add_message(uuid):
    """
    This route will be accessed remotely from the Chrome extension. It takes the user
    input (which is the Reddit submission's title and text and runs a prediction on it
    based on our previously trained model. Then it returns the results back to the
    extension so it can display them.
    """
    content = request.json
    print(content)
    title = content['title']
    text = content['text']
    X = title + ' ' + text
    wwwdir = '/var/www/apache-flask/application'
    clf = load(wwwdir + '/pipeline.gz')
    argsorted_probs = clf.predict_proba([doc]).argsort()[0][::-1]
    sorted_classes = clf.classes_[argsorted_probs]
    selected_predictions = list(sorted_classes[:3])
    return jsonify({"result": [selected_predictions]})

if __name__ == '__main__':
    app.run(host= '0.0.0.0',debug=True)
