import os
import re
import sys
import time
import pickle

from datetime import datetime
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from subscribe import cts
from collections import OrderedDict
from subscribe import helper as h


def get_text_from_path(root_path, relative_path):
    complete_path = os.path.join(root_path, relative_path, os.path.basename(relative_path) + '.txt')
    try:
        return open(complete_path, encoding='UTF-8').read()
    except FileNotFoundError:
        return ''


def get_text_corpus(path, toy=False):
    """
    Args:
        path: RESUMES_PATH
        toy: Boolean indicating whether should take the real data or a toy example.
    Returns: OrderedDict with the
    """
    if not toy:
        text_dict = [(int(os.path.basename(relative_path)), get_text_from_path(path, relative_path))
                     for relative_path in os.listdir(path) if os.path.isdir(os.path.join(path, relative_path))]
        text_dict = OrderedDict(text_dict)
    else:
        # Small data set to understand algorithms
        text_dict = OrderedDict([(1, 'common juan pedro'),
                                 (2, 'common camilo'),
                                 (3, 'common alberto high high high high'),
                                 (4, '')])

    # filter any numbers:
    for user_id, text in text_dict.items():
        # TODO: what about letters number combinations such as 'python3'
        text_dict[user_id] = re.sub(r'\d+', '',  text)

    return text_dict


def get_text_stats(path, use_idf):
    """
    Gets tf_idf transformed data and the vocabulary
    Args:
        path: The directory of the resumes
    Returns: Tuple containing Sparse Matrix with tf_idf data,  vocabulary dictionary and text_corpus (OrderedDict)
    """
    count_vectorizer = CountVectorizer()
    text_corpus_dict = get_text_corpus(path, toy=False)
    data_counts = count_vectorizer.fit_transform([e for e in text_corpus_dict.values()])
    tf_transformer = TfidfTransformer(use_idf=use_idf).fit(data_counts)

    data_tf_idf = tf_transformer.transform(data_counts)
    vocabulary = count_vectorizer.vocabulary_

    return data_tf_idf, vocabulary, text_corpus_dict


def save_relevance_dictionary(path):
    """
    For each word it will get a score of how desirable it is to add the search criteria.
    This is useful for the autocomplete.
    """

    data_tf_idf, vocabulary, text_corpus = get_text_stats(path, use_idf=False)

    scores = []
    for word_str, word_num_code in vocabulary.items():

        corpus_length = len(text_corpus)

        # short words will have 0 score.
        if corpus_length == 0 or len(word_str) < 4:
            score = 0
        else:

            col = data_tf_idf.getcol(word_num_code)

            height = col.shape[0]
            sqr = col.copy()  # take a copy of the col
            sqr.data **= 2  # square the data, i.e. just the non-zero data

            mean = col.mean()
            variance = sqr.sum()/height - mean**2

            score = mean + variance

        scores.append((word_str, score))

    scores.sort(key=lambda x: x[1])

    pickle.dump({k: v for k, v in scores}, open('relevance_dictionary.p', 'wb'))


def add_position_effect(text, relevance, word):
    """
    The relevance has a n additional factor: A word near the top of the document should be more
    important than at the bottom.
    Args:
        text: string
        relevance: float
        word: string
    Returns: modified relevance
    """

    if len(text) > 0:
        position_percent = (len(text) - text.lower().find(word))/len(text)
        relevance *= position_percent

    return relevance


def save_user_relevance_dictionary(path):
    """
    For each word finds the user_id relevance. This is the data structure:
    word_user_dict = {
        'word_1': ((user_id_1, relevance_1), (user_id_2, relevance_2) q)
    }
    Args:
        path: The directory of the resumes
    Returns: Saves file with dictionary
    """
    data_tf_idf, vocabulary, text_corpus = get_text_stats(path, use_idf=True)

    user_relevance_dictionary = {}
    for word, num_word in vocabulary.items():
        values = []
        for document, user_id in enumerate(text_corpus.keys()):

            relevance = data_tf_idf[document, num_word]

            if relevance > 0:
                relevance = add_position_effect(text_corpus[user_id], relevance, word)
                values.append((int(user_id), relevance))

            user_relevance_dictionary[word] = tuple(values)

    user_relevance_dictionary = h.remove_accents(user_relevance_dictionary)

    pickle.dump(user_relevance_dictionary, open('word_user_dictionary.p', 'wb'))


def run():
    sys.stdout = h.Unbuffered(open('search_engine.log', 'a'))

    h.log("STARTED RELEVANCE DICT")
    t0 = time.time()
    save_relevance_dictionary(cts.RESUMES_PATH)
    t1 = time.time()
    h.log('RELEVANCE DICTIONARY, time: {}'.format(t1 - t0))

    h.log("STARTED USER RELEVANCE DICT")
    t0 = time.time()
    save_user_relevance_dictionary(cts.RESUMES_PATH)
    t1 = time.time()
    h.log('USER RELEVANCE DICTIONARY, time: {}'.format(t1 - t0))


if __name__ == "__main__":
    run()
