from app import app
from flask import Flask, request, jsonify
from joblib import load

# TODO: Only suggests one subreddit currently. Want to suggest at least a few.

@app.route('/api/add_message/<uuid>', methods=['GET', 'POST'])
def add_message(uuid):
    content = request.json
    print(content)
    title = content['title']
    text = content['text']
    X = title + ' ' + text
    wwwdir = '/var/www/apache-flask/application'
    clf = load(wwwdir + '/pipeline.gz')
    prediction = clf.predict([X])[0]
    return jsonify({"result": prediction})

if __name__ == '__main__':
    app.run(host= '0.0.0.0',debug=True)
