# scripts/helpers.py
import re, html
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from datetime import datetime

STOP = set(stopwords.words("english"))
LEM = WordNetLemmatizer()

url_re = re.compile(r'https?://\S+|www\.\S+')
html_re = re.compile(r'<.*?>')
emoji_re = re.compile("["
                      u"\U0001F600-\U0001F64F"
                      u"\U0001F300-\U0001F5FF"
                      u"\U0001F680-\U0001F6FF"
                      u"\U0001F1E0-\U0001F1FF"
                      "]+", flags=re.UNICODE)

def clean_text(text):
    if not text:
        return ""
    t = str(text)
    t = html.unescape(t)
    t = url_re.sub(" ", t)
    t = html_re.sub(" ", t)
    t = emoji_re.sub(" ", t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def preprocess(text):
    t = clean_text(text).lower()
    tokens = word_tokenize(t)
    tokens = [w for w in tokens if w.isalpha() and w not in STOP]
    lemmas = [LEM.lemmatize(w) for w in tokens]
    return " ".join(lemmas)

def now_ts():
    return datetime.utcnow().isoformat() + "Z"
