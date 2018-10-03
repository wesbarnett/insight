# Selects regularization parameters using a grid search. Then tests the best parameter
# selected using a hold out test set. From there the model is retrained on the entire
# data set.

# Author : Wes Barnett

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

class redditSGDModel:

    def __init__(self, engine, model):

        self.cv_chunks = model["cv_chunks"]
        self.chunksize = model["chunksize"]
        self.table_name = model["table_name"]
        self.subscribers_ulimit = model["subscribers_ulimit"]
        self.subscribers_llimit = model["subscribers_llimit"]

        self.vectorizer = HashingVectorizer(
            decode_error="ignore", analyzer=nlp_scripts.stemmed_words, n_features=2**18,
            alternate_sign=False, norm="l1", stop_words="english"
        )

        self.engine = engine


def parse_data_chunk(chunk, vectorizer):
    """
    Parses the information in the pandas Dataframe chunk and vectorizes it for use with
    sklearn models.

    chunk : pandas Dataframe chunk from generator
    vectorizer : the vectorizer to be used for featurization

    Returns the features (X) and the labels (y).
    """

    X = chunk["title"] + " " + chunk["selftext"]
    y = chunk["subreddit"]
    del chunk
    X = vectorizer.transform(X)
    return X, y

def train_val_model(engine, alpha, model, vectorizer, classes, f):
    """
    Trains a linear SVM using stochastic gradient descent using the data in the SQL
    table specified. The test set and the validation set are skipped in this function.

    engine : sqlalchemy connection to database
    alpha : the regularization parameter
    model : model parameters from configuration file
    f : connection to log file

    Returns the trained sklearn model.
    """

    cv_chunks = model["cv_chunks"]
    chunksize = model["chunksize"]
    table_name = model["table_name"]

    sgd_cv = SGDClassifier(alpha=alpha, n_jobs=3, max_iter=1000, tol=1e-3,
            random_state=0)

    # "by index" is very important such that we always skip the same test and validation
    # sets.
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

def eval_val_model(sgd_cv, engine, model, vectorizer, f):
    """
    Evaluates the model that was trained using 'train_val_model'. Skips the test set,
    but reads in the validation set for evaluation.

    sgd_cv : sklearn model trained with 'train_val_model'
    engine : sqlalchemy connection to database
    model : model parameters from configuration file
    f : connection to log file

    Returns the score.
    """

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

def grid_search(engine, alpha_range, model, vectorizer, classes, f):

    # Grid search
    best_score = 0.
    f.write("Training models...\n")
    f.flush()
    for alpha in alpha_range:

        sgd_cv = train_val_model(engine, alpha, model, vectorizer, classes, f)
        score = eval_val_model(sgd_cv, engine, model, vectorizer, classes, f)
        if score > best_score:
            best_score = score
            best_alpha = alpha

    f.write(f"best alpha = {best_alpha}\n")
    f.write(f"best val score= {best_score}\n")
    f.flush()

    del sgd_cv

    return best_alpha

def get_classes(engine, model):
    """
    Gets the number of classes in a grouping for subreddits based on the number of
    subscribers.

    engine : sqlalchemy connection to database
    model : model read in from configuration file

    Return number of classes.
    """

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

def train_all_data(engine, best_alpha, model, vectorizer, classes, f):

    chunksize = model["chunksize"]
    table_name = model["table_name"]

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

    return sgd

def train_train_data(engine, best_alpha, model, vectorizer, classes, f):

    chunksize = model["chunksize"]
    table_name = model["table_name"]

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

        X_train, y_train = parse_data_chunk(chunk, vectorizer)
        sgd_train.partial_fit(X_train, y_train, classes)

        train_score = sgd_train.score(X_train, y_train)
        train_f1_score = f1_score(y_train, sgd_train.predict(X_train), average='weighted')
        test_score = sgd_train.score(X_test, y_test)
        test_f1_score = f1_score(y_test, sgd_train.predict(X_test), average='weighted')

        i += chunk.shape[0]
        f.write(f"{i} {train_score} {test_score} {train_f1_score} {test_f1_score}\n")
        f.flush()

        del X_train
        del y_train


if __name__ == "__main__":

    db_user = "wes"
    db_name = "reddit_db"
    json_config = "models.json"
    logfile = "log"

    # Load model parameters
    with open(json_config) as jsonfile:
        models = json.load(jsonfile)

    f = open(logfile, "a")
    f.write('\n')
    f.write(time.ctime())
    f.write('\n')

    engine = sqlalchemy.create_engine(f"postgresql://{db_user}@localhost/{db_name}")

    for key, model in models.items():

        vectorizer = HashingVectorizer(
            decode_error="ignore", analyzer=nlp_scripts.stemmed_words, n_features=2**18,
            alternate_sign=False, norm="l1", stop_words="english"
        )

        classes = get_classes(engine, model)
        f.write(f"Number of classes: {classes.shape[0]}\n")
        f.flush()

        alpha_range = np.logspace(-7,-3,5)
        best_alpha = grid_search(engine, alpha_range, model, vectorizer, classes, f)

        sgd_train = train_train_data(engine, best_alpha, model, vectorizer, classes, f)
        dump(sgd_train.sparsify(), model["train_outfile"])
        del sgd_train
        
        sgd = train_all_data(engine, best_alpha, model, vectorizer, classes, f)
        dump(sgd.sparsify(), model["outfile"])
        del sgd

    engine.dispose()

    f.close()
