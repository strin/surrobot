# some basic algorithms to embed an email to a vector.
# a document is a list of words, with stopwords removed.
import numpy as np

WORD2VEC_MODEL = None
def init_word2vec():
    global WORD2VEC_MODEL
    from gensim.models import Word2Vec
    WORD2VEC_MODEL = Word2Vec.load_word2vec_format('model/GoogleNews-vectors-negative300.bin', binary=True)

def avg_word_vec(doc):
    vec = np.zeros_like(WORD2VEC_MODEL['hello'])
    count = 0
    for word in doc:
        try:
            vec += WORD2VEC_MODEL[word]
            count += 1
        except KeyError:
            pass

    return vec / float(count)



