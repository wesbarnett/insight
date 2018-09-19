import matplotlib.pyplot as plt
import nlp_scripts
import numpy as np
import pandas as pd
from joblib import dump, Memory
from sklearn.feature_extraction.text import CountVectorizer, HashingVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.multiclass import OneVsRestClassifier
from sklearn.naive_bayes import BernoulliNB, MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelBinarizer
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
#    and subscribers < {subscribers_ulimit};""",
    engine,
)
engine.dispose()

vectorizer = HashingVectorizer(
    decode_error="ignore", analyzer=nlp_scripts.stemmed_words, n_features=2 ** 18,
    alternate_sign=False
)

print(f"Number of classes: {classes.shape[0]}")

#nb = MultinomialNB()
sgd = SGDClassifier()

i = 0
for chunk in df:

    X = chunk["title"] + " " + chunk["selftext"]
    y = chunk["subreddit"]

    X = vectorizer.transform(X)

    sgd.partial_fit(X, y, classes)

    i += chunk.shape[0]
    print(i)

dump(sgd, "sgd.gz")
