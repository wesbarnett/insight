import nlp_scripts
import numpy as np
import pandas as pd
from joblib import dump
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split, GridSearchCV
import sqlalchemy
import sql_scripts

subscribers_ulimit = None
subscribers_llimit = 1e5

cv_chunks = 1
chunksize = 1e4

# Select only subreddits with minimum number of submissions
engine = sqlalchemy.create_engine("postgresql://wes@localhost/reddit_db")

classes = pd.read_sql(
    f"""
    select display_name from subreddits 
    where subscribers > {subscribers_llimit};""",
    engine,
)

vectorizer = HashingVectorizer(
    decode_error="ignore", analyzer=nlp_scripts.stemmed_words, n_features=2**18,
    alternate_sign=False
)

print(f"Number of classes: {classes.shape[0]}")

df = pd.read_sql("select * from submissions_large limit 50000;", engine,
        chunksize=chunksize)

# Hold out test set (8 chunks)
print("Writing test set to disk...")
for i in range(cv_chunks):
    chunk = next(df)
    X_test = chunk["title"] + " " + chunk["selftext"]
    y_test = chunk["subreddit"]
    del chunk
    X_test = vectorizer.transform(X_test)
    dump((X_test, y_test), "test_set_"+str(i))
    del X_test
    del y_test

# Validation set (8 chunks)
for i in range(cv_chunks):
    chunk = next(df)
    del chunk

sgd_cv_scores = {}
print("Training models...")
for alpha in np.logspace(-7,-1,7):

    print(f"alpha = {alpha}")
    # Logistic Regression because we want probabilities; default is SVM
    sgd_cv = SGDClassifier(alpha=alpha, n_jobs=3, loss="log", max_iter=1000, tol=1e-3)

    df = pd.read_sql("select * from submissions_large limit 50000;", engine,
            chunksize=chunksize)

    # Skip hold out test set (8 chunks = 80,000 submissions)
    for i in range(cv_chunks):
        chunk = next(df)
        del chunk

    # Skip validation set (8 chunks = 80,000 submissions)
    for i in range(cv_chunks):
        chunk = next(df)
        del chunk

    j = 0
    for chunk in df:

        j += chunk.shape[0]
        print(j)

        X_train = chunk["title"] + " " + chunk["selftext"]
        y_train = chunk["subreddit"]
        del chunk

        X_train = vectorizer.transform(X_train)

        sgd_cv.partial_fit(X_train, y_train, classes)

        del X_train
        del y_train

    dump(sgd_cv, "sgd_cv_"+str(i))

    df = pd.read_sql("select * from submissions_large limit 50000;", engine,
            chunksize=chunksize)

    # Skip hold out test set
    for j in range(cv_chunks):
        chunk = next(df)
        del chunk

    # Validation set
    print("Calculating validation score...")
    sgd_cv_scores[alpha] = []
    score_avg = 0
    for j in range(cv_chunks):

        chunk = next(df)

        X_val = chunk["title"] + " " + chunk["selftext"]
        y_val = chunk["subreddit"]
        del chunk

        X_val = vectorizer.transform(X_val)

        score = sgd_cv.score(X_val, y_val)

        del X_val
        del y_val

        score_avg += score
        sgd_cv_scores[alpha].append(score)

    score_avg /= cv_chunks
    print(f"val score = {score_avg}")

dump(sgd_cv_scores, "sgd_cv_scores")

engine.dispose()
