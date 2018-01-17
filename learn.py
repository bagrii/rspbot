# learn.py
# Convert a collection of Reddit submission titles to a matrix of tokens occurrences

import pickle

from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.metrics.pairwise import linear_kernel
from scipy.sparse import vstack


def get_tokens_vector(corpus):
    hv = HashingVectorizer(analyzer='word', stop_words = 'english')
    tok_vector = hv.fit_transform(corpus)
    return tok_vector

def get_similar_items_index(index, tok_vector, n = 5, score = 0.5):
    similarities = linear_kernel(tok_vector[index:index + 1], tok_vector).flatten()
    # sort and reverse
    similar_indexes = similarities.argsort()[::-1]
    for i in similar_indexes[0:n]:
        if i != index and similarities[i] >= score:
            yield i, similarities[i]

def get_similar_items(corpus, index, tok_vector):
    for i, _ in get_similar_items_index(index, tok_vector):
        yield corpus[i]

def update_token_vector(tok_vector, tok_vector_new):
    return vstack([tok_vector, tok_vector_new])

def save_token_vector(file_name, tok_vector):
    with open(file_name, "wb") as fp:
        pickle.dump(tok_vector, fp)

def load_token_vector(file_name):
    with open(file_name, "rb") as fp:
        return pickle.load(fp)
