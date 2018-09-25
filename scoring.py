import nlp_scripts
import numpy as np
import pandas as pd
from joblib import load
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split, GridSearchCV
import sqlalchemy
import sql_scripts

def parse_data_chunk(chunk, vectorizer):
    X = chunk["title"] + " " + chunk["selftext"]
    y = chunk["subreddit"]
    del chunk
    X = vectorizer.transform(X)
    return X, y

# 711014
model_large = {"subscribers_ulimit": None, "subscribers_llimit": 1.3e5, "cv_chunks": 1,
        "chunksize": 7e4, "table_name": "submissions_0", "outfile":
        "MODELS_L1_NORM/sgd_svm_large.gz", "train_outfile": "MODELS_L1_NORM/sgd_svm_train_large.gz"
        }

# 452885
model_med = {"subscribers_ulimit": 1.3e5, "subscribers_llimit": 5.5e4, "cv_chunks": 1,
        "chunksize": 4e4, "table_name": "submissions_1", "outfile":
        "MODELS_L1_NORM/sgd_svm_med.gz", "train_outfile": "MODELS_L1_NORM/sgd_svm_train_med.gz"
        }

# 209340
model_small = {"subscribers_ulimit": 5.5e4, "subscribers_llimit": 3.3e4, "cv_chunks": 1,
        "chunksize": 2e4, "table_name": "submissions_2", "outfile":
        "MODELS_L1_NORM/sgd_svm_small.gz", "train_outfile": "MODELS_L1_NORM/sgd_svm_train_small.gz"
        }

models = [model_small, model_med, model_large]

vectorizer = HashingVectorizer(
    decode_error="ignore", analyzer=nlp_scripts.stemmed_words, n_features=2**18,
    alternate_sign=False, stop_words="english", norm="l1"
)

engine = sqlalchemy.create_engine("postgresql://wes@localhost/reddit_db")

for model in models:

    subscribers_ulimit = model["subscribers_ulimit"]
    subscribers_llimit = model["subscribers_llimit"]
    cv_chunks = model["cv_chunks"]
    chunksize = model["chunksize"]
    table_name = model["table_name"]
    outfile = model["outfile"]
    train_outfile = model["train_outfile"]

    if subscribers_ulimit == None:
        classes = pd.read_sql(
            f"""
            select display_name from subreddits 
            where subscribers > {subscribers_llimit};""",
            engine,
        )
    else:
        classes = pd.read_sql(
            f"""
            select display_name from subreddits 
            where subscribers <= {subscribers_ulimit}
            and subscribers > {subscribers_llimit};""",
            engine,
        )

    print(classes.shape[0])

    df = pd.read_sql(f"select * from {table_name};", engine,
            chunksize=chunksize)

    chunk = next(df)
    X, y_true = parse_data_chunk(chunk, vectorizer)

    sgd = load(train_outfile)

    argsorted_dec = sgd.decision_function(X).argsort(axis=1)
    sorted_classes = sgd.classes_[argsorted_dec]

    score = 0.0
    top_n = 1
    for top_n in range(1,6):
        print(f"Top {top_n} mean accuracy:")
        for i,j in enumerate(sorted_classes):
            if y_true[i] in j.ravel()[::-1][0:top_n]:
                score += 1.0
        score /= y_true.shape[0] 
        print(score)

#   print(score)
#   print(sgd.score(X, y_true))
