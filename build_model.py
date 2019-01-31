# Selects regularization parameters using a grid search. Then tests the best parameter
# selected using a hold out test set. From there the model is retrained on the entire
# data set.

# Author : Wes Barnett

import time
import json

from joblib import dump
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import f1_score
import sqlalchemy

import nlp_scripts


def parse_data_chunk(chunk, vectorizer):
    """Parses the information in the pandas Dataframe chunk and vectorizes it for use with
    sklearn models.

    Parameters
    ----------
    chunk : pandas Dataframe
        Chunk from generator read in from SQL database.
    vectorizer : sklearn HashingVectorizer object
        The vectorizer to be used for featurization.

    Return
    ------
    X : scipy.sparse matrix, shape = (chunk.shape[0], self.n_features)
        Document-term matrix.
    y : pandas Series
        Class labels.
    """

    X = chunk["title"] + " " + chunk["selftext"]
    y = chunk["subreddit"]
    X = vectorizer.transform(X)
    return X, y


def train_val_model(engine, alpha, model, vectorizer, classes, logfile_object):
    """Trains a linear SVM using stochastic gradient descent using the data in the SQL
    table specified. The test set and the validation set are skipped in this function.

    Parameters
    ----------
    engine : sqlalchemy connection to database
    alpha : float
        The regularization parameter.
    model : dictionary
        Model parameters from configuration file.
    vectorizer : sklearn HashingVectorizer object
        The vectorizer to be used for featurization.
    f : connection to log file

    Returns
    -------
    sgd_cv : sklearn SGDClassifier model.
    """

    cv_chunks = model["cv_chunks"]
    chunksize = model["chunksize"]
    table_name = model["table_name"]

    sgd_cv = SGDClassifier(
        alpha=alpha, n_jobs=3, max_iter=1000, tol=1e-3, random_state=0
    )

    # "by index" is very important such that we always skip the same test and validation
    # sets.
    df = pd.read_sql(
        f"select * from {table_name} order by index;", engine, chunksize=chunksize
    )

    # Skip hold out test set and validation set
    for i in range(cv_chunks * 2):
        chunk = next(logfile_object)
        print(chunk.iloc[0])

    j = 0
    for chunk in df:

        j += chunk.shape[0]
        logfile_object.write(f"{j}\n")
        logfile_object.flush()

        X_train, y_train = parse_data_chunk(chunk, vectorizer)

        sgd_cv.partial_fit(X_train, y_train, classes)

    return sgd_cv


def eval_val_model(sgd_cv, engine, model, vectorizer, logfile_object):
    """Evaluates the model that was trained using 'train_val_model'. Skips the test set,
    but reads in the validation set for evaluation.

    Parameters
    ----------
    sgd_cv : sklearn SGDClassifier object
        model trained with 'train_val_model'
    engine : sqlalchemy connection to database
    model : dictionary
        Model parameters from configuration file.
    vectorizer : sklearn HashingVectorizer object
        The vectorizer to be used for featurization.
    f : connection to log file

    Returns
    -------
    score_avg : float
        Average score of model on validation set.
    """

    cv_chunks = model["cv_chunks"]
    chunksize = model["chunksize"]
    table_name = model["table_name"]

    # Re-read from beginning of table
    df = pd.read_sql(
        f"select * from {table_name} order by index;", engine, chunksize=chunksize
    )

    # Skip hold out test set
    for j in range(cv_chunks):
        chunk = next(logfile_object)

    # Validation set scoring
    logfile_object.write("Calculating validation score...\n")
    logfile_object.flush()
    score_avg = 0.
    for chunk in range(cv_chunks):

        chunk = next(logfile_object)

        X_val, y_val = parse_data_chunk(chunk, vectorizer)

        score = sgd_cv.score(X_val, y_val)
        logfile_object.write(f"accuracy = {score}\n")
        score = f1_score(y_val, sgd_cv.predict(X_val), average="weighted")
        logfile_object.write(f"f1 score = {score}\n")

        score_avg += score

    score_avg /= cv_chunks

    logfile_object.write(f"alpha = {alpha}\n")
    logfile_object.write(f"val score = {score_avg}\n")
    logfile_object.flush()

    return score_avg


def grid_search(engine, alpha_range, model, vectorizer, classes, logfile_object):
    """ Performs grid search on the data set, holding out the validation and test sets.

    Parameters
    ----------
    engine : sqlalchemy connection to database
    alpha_range : list of floats
        Range of regularization parameters to test.
    model : dictionary
        Model parameters from configuration file.
    vectorizer : sklearn HashingVectorizer object
        The vectorizer to be used for featurization.
    classes : pandas Series
        All possible classes in this subset.
    f : connection to log file

    Returns
    -------
    best_alpha : float
        The best regularization parameter based on validation set performance.
    """

    best_score = 0.
    logfile_object.write("Training models...\n")
    logfile_object.flush()
    for alpha in alpha_range:

        sgd_cv = train_val_model(engine, alpha, model, vectorizer, classes, logfile_object)
        score = eval_val_model(sgd_cv, engine, model, vectorizer, classes, logfile_object)
        if score > best_score:
            best_score = score
            best_alpha = alpha

    logfile_object.write(f"best alpha = {best_alpha}\n")
    logfile_object.write(f"best val score= {best_score}\n")
    logfile_object.flush()

    return best_alpha


def get_classes(engine, model):
    """Gets the number of classes in a grouping for subreddits based on the number of
    subscribers.

    Parameters
    ----------
    engine : sqlalchemy connection to database
    model : dictionary
        Model parameters from configuration file.

    Returns
    -------
    classes : pandas Series
        List of classes in subset of data.
    """

    subscribers_ulimit = model["subscribers_ulimit"]
    subscribers_llimit = model["subscribers_llimit"]

    if subscribers_ulimit is None:
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


def train_all_data(engine, best_alpha, model, vectorizer, classes, logfile_object):
    """Trains the model on the entire training set.

    Parameters
    ----------
    engine : sqlalchemy connection to database
    best_alpha : the regularization parameter chosen from grid search
    model : model parameters from configuration file
    vectorizer : sklearn HashingVectorizer object
        The vectorizer to be used for featurization.
    classes : all possible classes
    f : connection to log file

    Returns
    -------
    sgd : sklearn SGDClassifier model.
    """

    chunksize = model["chunksize"]
    table_name = model["table_name"]

    # Entire data set
    sgd = SGDClassifier(
        alpha=best_alpha, n_jobs=3, max_iter=1000, tol=1e-3, random_state=0
    )
    logfile_object.write("Performing training on entire data set...\n")
    logfile_object.flush()

    df = pd.read_sql(
        f"select * from {table_name} order by index;", engine, chunksize=chunksize
    )

    j = 0
    for chunk in df:

        j += chunk.shape[0]
        logfile_object.write(f"{j}\n")
        logfile_object.flush()

        X, y = parse_data_chunk(chunk, vectorizer)
        sgd.partial_fit(X, y, classes)

    return sgd


def train_training_data(engine, best_alpha, model, vectorizer, classes, logfile_object):
    """Trains the model on just the training set.

    Parameters
    ----------
    engine : sqlalchemy connection to database
    best_alpha : the regularization parameter chosen from grid search
    model : model parameters from configuration file
    vectorizer : sklearn HashingVectorizer object
        The vectorizer to be used for featurization.
    classes : all possible classes
    f : connection to log file

    Returns
    -------
    sgd_train : sklearn SGDClassifier model.
    """

    chunksize = model["chunksize"]
    table_name = model["table_name"]

    logfile_object.write("Performing training on entire training set...\n")
    logfile_object.flush()

    df = pd.read_sql(
        f"select * from {table_name} order by index;", engine, chunksize=chunksize
    )

    sgd_train = SGDClassifier(
        alpha=best_alpha, n_jobs=3, max_iter=1000, tol=1e-3, random_state=0
    )

    chunk = next(logfile_object)  # Skip hold out test set
    print(chunk.iloc[0])
    X_test, y_test = parse_data_chunk(chunk, vectorizer)

    logfile_object.write(f"N  train_score test_score train_f1_Score test_f1_score\n")
    logfile_object.flush()

    i = 0
    for chunk in df:

        X_train, y_train = parse_data_chunk(chunk, vectorizer)
        sgd_train.partial_fit(X_train, y_train, classes)

        train_score = sgd_train.score(X_train, y_train)
        train_f1_score = f1_score(
            y_train, sgd_train.predict(X_train), average="weighted"
        )
        test_score = sgd_train.score(X_test, y_test)
        test_f1_score = f1_score(y_test, sgd_train.predict(X_test), average="weighted")

        i += chunk.shape[0]
        logfile_object.write(f"{i} {train_score} {test_score} {train_f1_score} {test_f1_score}\n")
        logfile_object.flush()

    return sgd_train


def train_training_data_dump(engine, best_alpha, model, vectorizer, classes, logfile_object):
    """Trains the model on just the training set and saves to disk.

    Parameters
    ----------
    engine : sqlalchemy connection to database
    best_alpha : the regularization parameter chosen from grid search
    model : model parameters from configuration file
    vectorizer : sklearn HashingVectorizer object
        The vectorizer to be used for featurization.
    classes : all possible classes
    f : connection to log file
    """

    sgd_train = train_training_data(engine, best_alpha, model, vectorizer, classes, logfile_object)
    dump(sgd_train.sparsify(), model["train_outfile"])


def train_all_data_dump(engine, best_alpha, model, vectorizer, classes, logfile_object):
    """Trains the model on the entire training set and saves to disk.

    Parameters
    ----------
    engine : sqlalchemy connection to database
    best_alpha : the regularization parameter chosen from grid search
    model : model parameters from configuration file
    vectorizer : sklearn HashingVectorizer object
        The vectorizer to be used for featurization.
    classes : all possible classes
    f : connection to log file
    """

    sgd = train_all_data(engine, best_alpha, model, vectorizer, classes, logfile_object)
    dump(sgd.sparsify(), model["outfile"])


if __name__ == "__main__":

    db_user = "wes"
    db_name = "reddit_db"
    json_config = "models.json"
    logfile = "log"

    # Load model parameters
    with open(json_config) as jsonfile:
        models = json.load(jsonfile)

    logfile_object = open(logfile, "a")
    logfile_object.write("\n")
    logfile_object.write(time.ctime())
    logfile_object.write("\n")

    engine = sqlalchemy.create_engine(f"postgresql://{db_user}@localhost/{db_name}")

    for key, model in models.items():

        vectorizer = HashingVectorizer(
            decode_error="ignore",
            analyzer=nlp_scripts.stemmed_words,
            n_features=2 ** 18,
            alternate_sign=False,
            norm="l1",
            stop_words="english",
        )

        # Get possible classes (subreddits)
        classes = get_classes(engine, model)
        logfile_object.write(f"Number of classes: {classes.shape[0]}\n")
        logfile_object.flush()

        # Do grid search
        alpha_range = np.logspace(-7, -3, 5)
        best_alpha = grid_search(engine, alpha_range, model, vectorizer, classes, logfile_object)

        train_training_data_dump(engine, best_alpha, model, vectorizer, classes, logfile_object)

        train_all_data_dump(engine, best_alpha, model, vectorizer, classes, logfile_object)

    engine.dispose()

    logfile_object.close()
