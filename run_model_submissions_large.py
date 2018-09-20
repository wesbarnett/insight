# Parameter selection using cross-validation

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

def parse_data_chunk(chunk):
    X = chunk["title"] + " " + chunk["selftext"]
    y = chunk["subreddit"]
    del chunk
    X = vectorizer.transform(X)
    return X, y

subscribers_ulimit = None
subscribers_llimit = 1e5

cv_chunks = 1
chunksize = 1e4

# For test set and validation set
limit = chunksize*cv_chunks*2

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

df = pd.read_sql(f"select * from submissions_large limit {limit};", engine,
        chunksize=chunksize)

# Hold out test set (8 chunks)
print("Skipping test and validation sets...")
for i in range(cv_chunks*2):
    chunk = next(df)

sgd_cv_scores = {}
best_score = 0.
print("Training models...")
# FIXME
#for i, alpha in enumerate(np.logspace(-7,-3,5)):
for i, alpha in enumerate(np.logspace(-7,-5,3)):

    # Logistic Regression because we want probabilities; default is SVM
    sgd_cv = SGDClassifier(alpha=alpha, n_jobs=3, loss="log", max_iter=1000, tol=1e-3)

#FIXME
    df = pd.read_sql("select * from submissions_large limit 50000;", engine,
            chunksize=chunksize)

    # Skip hold out test set and validation set
    for i in range(cv_chunks*2):
        chunk = next(df)
        del chunk

    j = 0
    for chunk in df:

        j += chunk.shape[0]
        print(j)

        X_train, y_train = parse_data_chunk(chunk)

        sgd_cv.partial_fit(X_train, y_train, classes)

        del X_train
        del y_train

    # Re-read from beginning of table
    df = pd.read_sql(f"select * from submissions_large limit {limit};", engine,
            chunksize=chunksize)

    # Skip hold out test set
    for j in range(cv_chunks):
        chunk = next(df)
        del chunk

    # Validation set scoring
    print("Calculating validation score...")
    sgd_cv_scores[alpha] = []
    score_avg = 0.
    for chunk in range(cv_chunks):

        chunk = next(df)

        X_val, y_val = parse_data_chunk(chunk)

        score = sgd_cv.score(X_val, y_val)
        if score > best_score:
            best_score = score
            best_alpha = alpha

        del X_val
        del y_val

        score_avg += score
        sgd_cv_scores[alpha].append(score)

    score_avg /= cv_chunks

    print(f"alpha = {alpha}")
    print(f"val score = {score_avg}")

print(f"best alpha = {best_alpha}")
print(f"best val score= {best_score}")

dump(sgd_cv_scores, "sgd_cv_scores")

del sgd_cv
del sgd_cv_scores

############## Training set (including validation set)
print("Performing training on entire training set...")

# FIXME
df = pd.read_sql(f"select * from submissions_large limit 50000;", engine,
        chunksize=chunksize)

sgd_train = SGDClassifier(alpha=best_alpha, n_jobs=3, loss="log", max_iter=1000, tol=1e-3)

# Skip test set
for i in range(cv_chunks):
    chunk = next(df)

i = 0
for chunk in df:
    i += chunk.shape[0]
    print(i)
    X_train, y_train = parse_data_chunk(chunk)
    sgd_train.partial_fit(X_train, y_train, classes)
    del X_train
    del y_train

df = pd.read_sql(f"select * from submissions_large limit {limit};", engine,
        chunksize=chunksize)

print("Getting average test score...")
score_avg = 0.
for i in range(cv_chunks):

    chunk = next(df)
    X_test, y_test = parse_data_chunk(chunk)
    score = sgd_train.score(X_test, y_test)

    del X_test
    del y_test

    score_avg += score

score_avg /= cv_chunks
print(f"test score = {score_avg}")
del sgd_train

############## Entire data set
sgd = SGDClassifier(alpha=best_alpha, n_jobs=3, loss="log", max_iter=1000, tol=1e-3)
print("Performing training on entire data set...")
# FIXME
df = pd.read_sql(f"select * from submissions_large limit 50000;", engine,
        chunksize=chunksize)

for chunk in df:

    j += chunk.shape[0]
    print(j)

    X, y = parse_data_chunk(chunk)

    sgd.partial_fit(X, y, classes)

    del X
    del y

# Save the model!
dump(sgd, "sgd.gz")

engine.dispose()
