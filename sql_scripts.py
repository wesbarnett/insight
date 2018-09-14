
import pandas as pd
import sqlalchemy

def convert_submissions_json_to_sql(datafile, database='reddit_db', db_user='wes'):
    """
    Converts Reddit json submissions file to SQL database
    datafile = name of Reddit json file
    """

    mykeys = ['author', 'created_utc', 'id', 'is_self', 'selftext',
            'subreddit', 'subreddit_subscribers', 'title']
    dtypes = {'author': sqlalchemy.types.Text, 'created_utc': sqlalchemy.types.Integer,
            'id': sqlalchemy.types.String(6), 'is_self': sqlalchemy.types.Boolean, 'selftext':
            sqlalchemy.types.Text, 'subreddit': sqlalchemy.types.Text,
            'subreddit_subscribers': sqlalchemy.types.Integer, 'title':
            sqlalchemy.types.Text, 'url': sqlalchemy.types.Text} 
    engine = sqlalchemy.create_engine(f'postgresql://{db_user}@localhost/{database}')
    reader = pd.read_json(datafile, lines=True, chunksize=10000, dtype=False)

    i = 0
    for chunk in reader:
        # Exclude submissions marked for over 18 and only include keys specified above
        chunk.loc[chunk['over_18'] == False, mykeys].to_sql('submissions', engine,
                if_exists='append', dtype=dtypes) 
        i += 1
        print(i)

    engine.dispose()

def convert_subreddits_json_to_sql(datafile='DATA/subreddits.json',
        database='reddit_db', db_user='wes'):
    """
    Converts Reddit json subreddits file to SQL database
    """
    mykeys = ['display_name', 'description']
    dtypes = {'display_name': sqlalchemy.types.Text, 'description': sqlalchemy.types.Text}
    engine = sqlalchemy.create_engine(f'postgresql://{db_user}@localhost/{database}')
    reader = pd.read_json(datafile, lines=True, chunksize=10000, dtype=False)

    i = 0
    for chunk in reader:
        # No adult content, only English, only public subreddits
        chunk.loc[(chunk['over18'] == False) & (chunk['subreddit_type'] == 'public') &
                (chunk['lang'] == 'en'), mykeys].to_sql('subreddits', engine,
                if_exists='append', dtype=dtypes) 
        i += 1
        print(i)

    engine.dispose()
