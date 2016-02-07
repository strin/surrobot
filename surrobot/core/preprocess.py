# preprocessing of emails.
import nltk

from nltk.corpus import stopwords
try:
    stopwords.words('english')
except LookupError:
    nltk.download('stopwords')

from nltk import word_tokenize
try:
    word_tokenize('hi')
except LookupError:
    nltk.download('punkt')

from nltk.corpus import wordnet
try:
    wordnet.synsets('hello')
except LookupError:
    nltk.download('wordnet')

def remote_stopwords(doc):
    return [word for word in doc if word not in stopwords.words('english')]

def remote_non_english(doc):
    return [word for word in doc if wordnet.synsets(word)]

def body2doc(email_body):
    # simple hack to extract main email body.
    email_body = email_body.replace('\r\n', '\n')
    email_body = email_body.replace('\r', '\n')
    dl_pos = email_body.find('\n\n\n')
    if dl_pos != -1:
        email_body = email_body[:dl_pos]

    # tokenize main body to get doc.
    doc = word_tokenize(email_body)
    doc = remote_non_english(doc)
    doc = remote_stopwords(doc)
    return doc



