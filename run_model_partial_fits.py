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

df = sql_scripts.query_submissions(
    subscribers_llimit=subscribers_llimit, subscribers_ulimit=subscribers_ulimit,
    chunksize=1e4
)

# Select only subreddits with minimum number of submissions
engine = sqlalchemy.create_engine("postgresql://wes@localhost/reddit_db")
classes = pd.read_sql(
    f"""
    select display_name from subreddits 
    where subscribers > {subscribers_llimit};""",
#   and subscribers < {subscribers_ulimit};""",
    engine,
)
engine.dispose()

vectorizer = HashingVectorizer(
    decode_error="ignore", analyzer=nlp_scripts.stemmed_words, n_features=2 ** 18,
    alternate_sign=False
)

print(f"Number of classes: {classes.shape[0]}")

# Logistic Regression because we want probabilities; default is SVM
sgd = SGDClassifier(n_jobs=3, loss="log", max_iter=1000, tol=1e-3)

#chunk = next(df)
#X_test = chunk["title"] + " " + chunk["selftext"]
#X_test = vectorizer.transform(X_test)
#y_test = chunk["subreddit"]

#sgd_stats = {}
#sgd_stats['accuracy_history'] = [0]
#sgd_stats['n_train'] = [0]

i = 0
for chunk in df:

    X_train = chunk["title"] + " " + chunk["selftext"]
    y_train = chunk["subreddit"]

    X_train = vectorizer.transform(X_train)

    sgd.partial_fit(X_train, y_train, classes)
#   sgd_stats['accuracy_history'].append(sgd.score(X_test, y_test))
#   sgd_stats['n_train'].append(sgd_stats['n_train'][-1] + chunk.shape[0])
#   print(sgd_stats['n_train'][-1], sgd_stats['accuracy_history'][-1])

    i += chunk.shape[0]
    print(i)

#dump(sgd_stats, "sgd_stats.gz")
dump(sgd, "sgd.gz")
