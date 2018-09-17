import matplotlib.pyplot as plt
import nlp_scripts
import numpy as np
import pandas as pd
from joblib import dump, Memory
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.multiclass import OneVsRestClassifier
from sklearn.naive_bayes import BernoulliNB
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelBinarizer
import sql_scripts

memory = Memory("./cachedir", verbose=10, compress=True)


@memory.cache
def get_data(subscribers_llimit=1e3, subscribers_ulimit=1e4, min_submissions=100):

    df = sql_scripts.query_submissions(subscribers_llimit, subscribers_ulimit)

    print(
        f"Minimum number of submissions for subreddit to be included: {min_submissions}"
    )

    subreddits_n = np.sum(df["subreddit"].value_counts() > min_submissions)
    print(f"Number of subreddits selected: {subreddits_n}")

    sublist = df["subreddit"].value_counts() > min_submissions
    df = df[df["subreddit"].isin(sublist[sublist].index.tolist())]

    print(f"Number of submissions selected: {df.shape[0]}")

    # TODO: Include title text
    X = df["selftext"]
    y = df["subreddit"]

    # Needed for OneVsRestClassifier
    lb = LabelBinarizer()
    y = lb.fit_transform(y)

    return X, y


X, y = get_data(1e3, 1e4, 500)

# TODO: stratify?
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)

# Multiclass format is not supported when doing ROC AUC, so targets need to be binarized
# (as above)
# https://stackoverflow.com/questions/26210471/scikit-learn-gridsearch-giving-valueerror-multiclass-format-is-not-supported#26210645
pipeline = make_pipeline(
    CountVectorizer(
        decode_error="ignore", binary=True, analyzer=nlp_scripts.stemmed_words
    ),
    OneVsRestClassifier(BernoulliNB()),
)

tuned_parameters = [{"countvectorizer__max_features": [1000, 2000]}]

clf_cv = GridSearchCV(
    pipeline,
    param_grid=tuned_parameters,
    scoring="roc_auc",
    return_train_score=True,
    verbose=10,
    n_jobs=2,
    cv=5,
)

clf_cv.fit(X_train, y_train)
dump(clf_cv, "clf_cv.gz")

y_score = clf_cv.predict_proba(X_test)
print(f"Test score: {roc_auc_score(y_test, y_score)}")

# Train model on entire data set
clf_best = clf_cv.best_estimator_.fit(X, y)
dump(clf_best, "clf_best.gz")
