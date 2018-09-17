import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sql_scripts
import nlp_scripts
from joblib import dump
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split, GridSearchCV

# from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import BernoulliNB
from sklearn.pipeline import make_pipeline
from sklearn.decomposition import PCA

df = sql_scripts.query_submissions(1e3, 1e4)
min_submissions = 100

print(f"Minimum number of submissions for subreddit to be included: {min_submissions}")

subreddits_n = np.sum(df["subreddit"].value_counts() > min_submissions)
print(f"Number of subreddits selected: {subreddits_n}")

sublist = df["subreddit"].value_counts() > min_submissions
df = df[df["subreddit"].isin(sublist[sublist].index.tolist())]

print(f"Number of submissions selected: {df.shape[0]}")

# TODO: Include title text
X = df["selftext"]
y = df["subreddit"]
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)

# This pipeline takes 7 minutes to run on my system when max_features = 200
# and about 281302 submissions selected and binary = True. Obviously those settings
# needs to change, but it's a benchmark.
# TODO: Use MulitnomialNB with binary = False
pipeline = make_pipeline(
    CountVectorizer(
        decode_error="ignore", binary=True, analyzer=nlp_scripts.stemmed_words,
        #TODO: remove and put in grid search
        max_features=200,
    ),
    BernoulliNB(),
)

# TODO: Grid search on max_features
#tuned_parameters = [{"countvectorizer__max_features": [200, 500, 1000, 2000]}]

#clf = GridSearchCV(
#    pipeline,
#    param_grid=tuned_parameters,
#    scoring="roc_auc",
#    return_train_score=True,
#    verbose=10,
#    n_jobs=3,
#    cv=5,
#)

#   clf.fit(X_train, y_train)
#   dump(clf, "clf.gz")

pipeline.fit(X_train, y_train)
dump(pipeline, "pipeline.gz")
