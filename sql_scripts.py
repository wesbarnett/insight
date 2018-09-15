
# Some useful functions for converting flat files from Reddit corpus into SQL database.
# Also includes function to query from Reddit SQL database.

# Data source: https://files.pushshift.io/reddit/

import pandas as pd
import sqlalchemy

def convert_submissions_json_to_sql(datafile, database="reddit_db", db_user="wes"):
    """Converts Reddit json submissions file to SQL database.

    Parameters
    ----------
    datafile : string
        Name of Reddit json file to be converted.
    database : string, optional, default: reddit_db
        Name of the SQL database where the file information will be stored.
    db_user : string, optional, default: wes
        Name of the SQL database user
    """

    mykeys = [
        "author",
        "created_utc",
        "id",
        "is_self",
        "selftext",
        "subreddit",
        "subreddit_subscribers",
        "title",
    ]
    dtypes = {
        "author": sqlalchemy.types.Text,
        "created_utc": sqlalchemy.types.Integer,
        "id": sqlalchemy.types.String(6),
        "is_self": sqlalchemy.types.Boolean,
        "selftext": sqlalchemy.types.Text,
        "subreddit": sqlalchemy.types.Text,
        "subreddit_subscribers": sqlalchemy.types.Integer,
        "title": sqlalchemy.types.Text,
        "url": sqlalchemy.types.Text,
    }
    engine = sqlalchemy.create_engine(f"postgresql://{db_user}@localhost/{database}")
    reader = pd.read_json(datafile, lines=True, chunksize=10000, dtype=False)

    i = 0
    for chunk in reader:
        # Exclude submissions marked for over 18 and only include keys specified above
        chunk.loc[chunk["over_18"] == False, mykeys].to_sql(
            "submissions", engine, if_exists="append", dtype=dtypes
        )
        i += 1
        print(i)

    engine.dispose()


def convert_subreddits_json_to_sql(
    datafile="DATA/subreddits.json", database="reddit_db", db_user="wes"
):
    """Converts Reddit json subreddits file to SQL database. Excludes adult content,
    non-English content, and private & archived subreddits.

    Parameters
    ----------
    datafile : string
        Name of json file containing subreddit information to be converted.
    database : string, optional, default: reddit_db
        Name of the SQL database where the file information will be stored.
    db_user : string, optional, default: wes
        Name of the SQL database user
    """
    mykeys = ["display_name", "description"]
    dtypes = {
        "display_name": sqlalchemy.types.Text,
        "description": sqlalchemy.types.Text,
    }
    engine = sqlalchemy.create_engine(f"postgresql://{db_user}@localhost/{database}")
    reader = pd.read_json(datafile, lines=True, chunksize=10000, dtype=False)

    i = 0
    for chunk in reader:
        # No adult content, only English, only public subreddits
        chunk.loc[
            (chunk["over18"] == False)
            & (chunk["subreddit_type"] == "public")
            & (chunk["lang"] == "en"),
            mykeys,
        ].to_sql("subreddits", engine, if_exists="append", dtype=dtypes)
        i += 1
        print(i)

    engine.dispose()


def query_submissions(
    subscribers_llimit=1000, subscribers_ulimit=1500, db="reddit_db", db_user="wes"
):
    """Queries the Reddit submission database. Only selects submissions from subreddits
    that have:
        * number subscribers within a specified range
        * not been deleted or removed
        * not labeled as over 18
        * English as language
        * status as public (not private or archived)
        * only contain a self post (text post)
    This list of subreddits comes from the table titled 'subreddits' in the same
    database.

    Parameters
    ----------
    subscribers_llimit : integer, optional, default: 1000
        Minimum number of subscribers for a subreddit to be included.
    subscribers_ulimit : integer, optional, default: 1500
        Maximum number of subscribers for a subreddit to be included.
    da : string, optional, default: reddit_db
        Name of the SQL database where the file information will be stored.
    db_user : string, optional, default: wes
        Name of the SQL database user
    """
    engine = sqlalchemy.create_engine(f"postgresql://{db_user}@localhost/{db}")
    df = pd.read_sql(
        f"""
        select * from submissions 
        where subreddit_subscribers > {subscribers_llimit} 
        and subreddit_subscribers < {subscribers_ulimit}
        and is_self = 'True' 
        and selftext <> '[deleted]' 
        and selftext <> '[removed]' 
        and subreddit in (select display_name from subreddits);""",
        engine,
    )
    engine.dispose()

    return df


# TODO: use this in Jupyter notebook??
def filter_by_min_submissions(df, min_submissions):
    """
    Only have submissions that are in subreddits that appear a minimum number of times
    in the data set.
    """

    sublist = df["subreddit"].value_counts() > min_submissions
    df = df[df["subreddit"].isin(sublist[sublist].index.tolist())]
    return df
