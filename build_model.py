# Parameter selection using cross-validation

import nlp_scripts
import numpy as np
import pandas as pd
from joblib import dump
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import f1_score
from datetime import date, time
import sqlalchemy
import sql_scripts
import time
import json
time.ctime()

# Test set is first ~10% of data. Validation is next ~10% of data.

def parse_data_chunk(chunk, vectorizer):
    X = chunk["title"] + " " + chunk["selftext"]
    y = chunk["subreddit"]
    del chunk
    X = vectorizer.transform(X)
    return X, y

def train_val_model(engine, alpha, model, f):

    cv_chunks = model["cv_chunks"]
    chunksize = model["chunksize"]
    table_name = model["table_name"]

    sgd_cv = SGDClassifier(alpha=alpha, n_jobs=3, max_iter=1000, tol=1e-3,
            random_state=0)

    df = pd.read_sql(f"select * from {table_name} order by index;", engine,
            chunksize=chunksize)

    # Skip hold out test set and validation set
    for i in range(cv_chunks*2):
        chunk = next(df)
        print(chunk.iloc[0])
        del chunk

    j = 0
    for chunk in df:

        j += chunk.shape[0]
        f.write(f"{j}\n")
        f.flush()

        X_train, y_train = parse_data_chunk(chunk, vectorizer)

        sgd_cv.partial_fit(X_train, y_train, classes)

        del X_train
        del y_train

    return sgd_cv

def eval_val_model(sgd_cv, engine, model, f):

    cv_chunks = model["cv_chunks"]
    chunksize = model["chunksize"]
    table_name = model["table_name"]

    # Re-read from beginning of table
    df = pd.read_sql(f"select * from {table_name} order by index;", engine,
            chunksize=chunksize)

    # Skip hold out test set
    for j in range(cv_chunks):
        chunk = next(df)
        del chunk

    # Validation set scoring
    f.write("Calculating validation score...\n")
    f.flush()
    score_avg = 0.
    for chunk in range(cv_chunks):

        chunk = next(df)

        X_val, y_val = parse_data_chunk(chunk, vectorizer)

        score = sgd_cv.score(X_val, y_val)
        f.write(f"accuracy = {score}\n")
        score = f1_score(y_val, sgd_cv.predict(X_val), average='weighted')
        f.write(f"f1 score = {score}\n")
        del X_val
        del y_val

        score_avg += score

    score_avg /= cv_chunks

    f.write(f"alpha = {alpha}\n")
    f.write(f"val score = {score_avg}\n")
    f.flush()

    return score_avg

def get_classes(engine, model):

    subscribers_ulimit = model["subscribers_ulimit"]
    subscribers_llimit = model["subscribers_llimit"]

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

    return classes

if __name__ == "__main__":

    db_user = "wes"
    db_name = "reddit_db"
    json_config = "models.json"
    logfile = "log"

    with open(json_config) as jsonfile:
        models = json.load(jsonfile)

    for i, j in models.items():
        print(i, j)
    exit()

    f = open(logfile, "a")
    f.write('\n')
    f.write(time.ctime())
    f.write('\n')

    vectorizer = HashingVectorizer(
        decode_error="ignore", analyzer=nlp_scripts.stemmed_words, n_features=2**18,
        alternate_sign=False, norm="l1", stop_words="english"
    )

    engine = sqlalchemy.create_engine(f"postgresql://{db_user}@localhost/{db_name}")

    for key, model in models.items():

        subscribers_ulimit = model["subscribers_ulimit"]
        subscribers_llimit = model["subscribers_llimit"]
        cv_chunks = model["cv_chunks"]
        chunksize = model["chunksize"]
        table_name = model["table_name"]
        outfile = model["outfile"]
        train_outfile = model["train_outfile"]

        classes = get_classes(engine, model)
        f.write(f"Number of classes: {classes.shape[0]}\n")
        f.flush()

        # Grid search
        best_score = 0.
        f.write("Training models...\n")
        f.flush()
        for alpha in np.logspace(-7,-3,5):

            sgd_cv = train_val_model(engine, alpha, model)
            score = eval_val_model(sgd_cv, engine, model, f)
            if score > best_score:
                best_score = score
                best_alpha = alpha

        f.write(f"best alpha = {best_alpha}\n")
        f.write(f"best val score= {best_score}\n")
        f.flush()

        del sgd_cv


        # Training set (including validation set)
        f.write("Performing training on entire training set...\n")
        f.flush()

        df = pd.read_sql(f"select * from {table_name} order by index;", engine,
                chunksize=chunksize)

        sgd_train = SGDClassifier(alpha=best_alpha, n_jobs=3, max_iter=1000, tol=1e-3,
                random_state=0)

        chunk = next(df) # Skip hold out test set
        print(chunk.iloc[0])
        X_test, y_test = parse_data_chunk(chunk, vectorizer)

        f.write(f"N  train_score test_score train_f1_Score test_f1_score\n")
        f.flush()

        i = 0
        for chunk in df:

            i += chunk.shape[0]
            X_train, y_train = parse_data_chunk(chunk, vectorizer)
            sgd_train.partial_fit(X_train, y_train, classes)

            train_score = sgd_train.score(X_train, y_train)
            train_f1_score = f1_score(y_train, sgd_train.predict(X_train), average='weighted')
            test_score = sgd_train.score(X_test, y_test)
            test_f1_score = f1_score(y_test, sgd_train.predict(X_test), average='weighted')

            f.write(f"{i} {train_score} {test_score} {train_f1_score} {test_f1_score}\n")
            f.flush()

            del X_train
            del y_train

        dump(sgd_train.sparsify(), train_outfile)
        del sgd_train


        # Entire data set
        sgd = SGDClassifier(alpha=best_alpha, n_jobs=3, max_iter=1000, tol=1e-3,
                random_state=0)
        f.write("Performing training on entire data set...\n")
        f.flush()

        df = pd.read_sql(f"select * from {table_name} order by index;", engine,
                chunksize=chunksize)

        j = 0
        for chunk in df:

            j += chunk.shape[0]
            f.write(f"{j}\n")
            f.flush()

            X, y = parse_data_chunk(chunk, vectorizer)

            sgd.partial_fit(X, y, classes)

            del X
            del y

        dump(sgd.sparsify(), outfile)
        del sgd

    engine.dispose()

    f.close()
