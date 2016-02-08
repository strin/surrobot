from surrobot.core.mail2vec import avg_word_vec, init_word2vec
from surrobot.core.preprocess import body2doc
from surrobot.db.db import EmailDB

import numpy as np
import numpy.linalg as npla

CACHE = dict()

def query_by_vec_online(table, vec, top_k=5):
    init_word2vec()
    db = EmailDB(table)
    scores = []
    for email in db.select():
        if email.message_id in CACHE:
            candidate_vec = CACHE[email.message_id]
        else:
            doc = body2doc(email.body)
            print '[cache doc]', doc
            candidate_vec = avg_word_vec(doc)
            CACHE[email.message_id] = candidate_vec
        score = np.dot(vec, candidate_vec) / npla.norm(vec) / npla.norm(candidate_vec) # cosine similarity.
        score = float(score)
        scores.append((email, score))

    scores = [pair for pair in scores if pair[1] == pair[1]]
    scores = sorted(scores, key=lambda pair: pair[1], reverse=True)

    print '[matched]', scores[:top_k]
    return scores[:top_k]

