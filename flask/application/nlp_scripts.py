# Some functions for NLP

from re import sub
from string import punctuation
from nltk.stem.snowball import SnowballStemmer
from nltk import word_tokenize
from nltk.corpus import stopwords

def process_text(txt):
    """Processes text in preparation for word stemming. Specifically it makes all
    letters lowercase, removes line breaks and tabs, and converts numbers, urls, email
    addresses, and dollar signs into symbolic characters. Removes additional
    punctuation.
    
    Parameters
    ----------
    txt : string
        The text to be processed.
    """

    # Make text all lowercase, remove line breaks and tabs
    txt = txt.lower()
    txt = sub("\n", " ", txt)
    txt = sub("\t", " ", txt)
    txt = sub("/", " ", txt)
    txt = sub("’", "", txt)

    # Convert numbers, urls, email addresses, and dollar signs
    txt = sub("[0-9]+", "number", txt)
    txt = sub("(http|https)://[^\s]*", "httpaddr", txt)
    txt = sub("[^\s]+@[^\s]+", "emailaddr", txt)
    txt = sub("[$]+", "dollar", txt)

    # Remove additional punctuation
    table = str.maketrans({key: None for key in punctuation})
    txt = txt.translate(table)

    return txt

def stemmed_words(doc):
    """Calls the text cleaner and then does stemming. This should be defined as the
    'analyzer' in CountVectorizer() when called later.
    
    Parameters
    ----------
    doc : string
        The text that will be processed and with words that will be stemmed.
    """
    doc = process_text(doc)
    stemmer = SnowballStemmer('english')
    tokens = word_tokenize(doc)
    stop = set(stopwords.words('english'))
    return (stemmer.stem(w) for w in tokens if w not in stop)
