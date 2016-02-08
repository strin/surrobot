# implement autoreply to emails.
from surrobot.core.mail2vec import avg_word_vec, init_word2vec
from surrobot.core.preprocess import body2doc
from surrobot.db.embedding import query_by_vec_online
from surrobot.db.db import EmailDB

from pprint import pprint

init_word2vec()

def query_by_body(body, top_k=5):
    ''' query top_k most probable replies based on raw email body '''
    doc = body2doc(body)
    print '[doc]', doc
    vec = avg_word_vec(doc)
    # retrieve top-k past inquery emails.
    candidates = query_by_vec_online('inbox', vec, top_k)
    # get past replies.
    db = EmailDB('outbox')
    replies = []
    for (email, score) in candidates:
        reply = db.select(
                    where='message_id=:message_id',
                    data=dict(message_id=email.message_id)
                )
        reply = list(reply)[0].body
        replies.append((reply, score))
    return replies


if __name__ == '__main__':
    pprint(query_by_body('I will start and deliver tomorrow.', top_k=5))

