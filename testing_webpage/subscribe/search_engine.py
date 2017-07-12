import os
import re
import pickle
import numpy as np

from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from cts import *
from collections import OrderedDict
import helper as h


def get_text_from_path(root_path, relative_path):
    complete_path = os.path.join(root_path, relative_path, os.path.basename(relative_path) + '.txt')
    try:
        return open(complete_path, encoding='UTF-8').read()
    except FileNotFoundError:
        return ''


def get_text_corpus(path, toy=False):

    if not toy:
        text_dict = [(int(os.path.basename(relative_path)), get_text_from_path(path, relative_path))
                     for relative_path in os.listdir(path) if os.path.isdir(os.path.join(path, relative_path))]
        text_dict = OrderedDict(text_dict)
    else:
        # Small data set to understand algorithms
        text_dict = OrderedDict([(1, 'common juan pedro'),
                                 (2, 'common camilo'),
                                 (3, 'common alberto high high high'),
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
    For each word it will get a score of how desirable is to add the search criteria.
    This is useful for the autocomplete.
    """

    data_tf_idf, vocabulary, text_corpus = get_text_stats(path, use_idf=False)

    scores = []
    for word_str, word_num_code in vocabulary.items():
        values = []
        for document in range(len(text_corpus)):
            v = data_tf_idf[document, word_num_code]
            values.append(v)

        a = np.array(values)

        if len(a) == 0 or len(word_str) < 4:
            score = 0
        else:
            score = np.mean(a) + np.std(a)

        scores.append((word_str, score))

    scores.sort(key=lambda x: x[1])
    #for word_str, score in scores:
    #    print('{}: {}'.format(word_str, score))

    pickle.dump({k: v for k, v in scores}, open('relevance_dictionary.p', 'wb'))


def save_user_relevance_dictionary(path):
    """
    For each word finds the user_id relevance. This is the data structure:
    word_user_dict = {
        'word_1': ((user_id_1, relevance_1), (user_id_2, relevance_2) ...)
    }
    Args:
        path: The directory of the resumes
    Returns: Saves file with dictionary
    """
    data_tf_idf, vocabulary, text_corpus = get_text_stats(path, use_idf=True)

    user_relevance_dictionary = {}
    for word, num_word in vocabulary.items():
        values = []
        for document, (user_id, text) in enumerate(text_corpus.items()):
            relevance = data_tf_idf[document, num_word]
            if relevance > 0:
                values.append((int(user_id), relevance))

        user_relevance_dictionary[word] = tuple(values)

    user_relevance_dictionary = h.remove_accents(user_relevance_dictionary)

    #for k, v in user_relevance_dictionary.items():
    #    print(k + ': ' + str(v))

    pickle.dump(user_relevance_dictionary, open('user_relevance_dictionary.p', 'wb'))


if __name__ == "__main__":
    save_relevance_dictionary(RESUMES_PATH)
    save_user_relevance_dictionary(RESUMES_PATH)
