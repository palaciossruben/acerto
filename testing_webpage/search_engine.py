import os
from django.core.wsgi import get_wsgi_application

# Environment can use the models as if inside the Django app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

import re
import sys
import nltk
import time
import pickle
import datetime

from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from collections import OrderedDict
from django.db.models import Q

from subscribe import helper as h
from subscribe import cts
from beta_invite.models import User


MAX_USERS_TO_UPDATE = 500


def get_word_array_lower_case_and_no_accents(search_text):
    """
    Args:
        search_text: string
    Returns: array with words
    """
    search_text = h.remove_accents_and_non_ascii(nltk.word_tokenize(search_text))

    # remove capital letters
    return [t.lower() for t in search_text]


def get_text_from_path(root_path, relative_path):
    complete_path = os.path.join(root_path, relative_path, os.path.basename(relative_path) + '.txt')
    try:
        return open(complete_path, encoding='UTF-8').read()
    except FileNotFoundError:
        return ''


def get_text_corpus():
    """
    Returns: OrderedDict with {user_id: text}
    """
    text_dict = [(u.id, u.curriculum_text) for u in User.objects.filter(~Q(curriculum_text=None)).all()]
    text_dict = OrderedDict(text_dict)

    # filter any numbers:
    for user_id, text in text_dict.items():
        # TODO: what about letters number combinations such as 'python3'
        text_dict[user_id] = re.sub(r'\d+', '',  text)

    return text_dict


def get_text_stats(use_idf):
    """
    tf (term frequency): counting terms (words)
    idf (inverse document frequency): rare words give more insights than common words on all documents
    Gets tf_idf transformed data and the vocabulary
    Returns: Tuple containing Sparse Matrix with tf_idf data,  vocabulary dictionary and text_corpus (OrderedDict)
    """
    count_vectorizer = CountVectorizer()
    text_corpus = get_text_corpus()
    data_counts = count_vectorizer.fit_transform([e for e in text_corpus.values()])
    tf_transformer = TfidfTransformer(use_idf=use_idf).fit(data_counts)

    data_tf_idf = tf_transformer.transform(data_counts)
    vocabulary = count_vectorizer.vocabulary_

    return data_tf_idf, vocabulary, text_corpus


def save_relevance_dictionary():
    """
    For each word it will get a score of how desirable it is to add the search criteria.
    This is useful for the autocomplete.
    """

    data_tf_idf, vocabulary, text_corpus = get_text_stats(use_idf=False)

    common_words = get_common_words(text_corpus)

    scores = []
    common_words = set(common_words)
    for word, word_num_code in vocabulary.items():

        if word in common_words:

            corpus_length = len(text_corpus)

            # short words will have 0 score.
            if corpus_length == 0 or len(word) < 4:
                score = 0
            else:

                col = data_tf_idf.getcol(word_num_code)

                height = col.shape[0]
                sqr = col.copy()  # take a copy of the col
                sqr.data **= 2  # square the data, i.e. just the non-zero data

                mean = col.mean()
                variance = sqr.sum()/height - mean**2

                score = mean + variance

            scores.append((word, score))

    scores.sort(key=lambda x: x[1])

    pickle.dump({k: v for k, v in scores}, open(cts.RELEVANCE_DICTIONARY, 'wb'))


def add_position_effect(text, relevance, word):
    """
    The relevance has an additional factor: A word near the top of the document should be more
    important than at the bottom.
    Args:
        text: string
        relevance: float
        word: string
    Returns: modified relevance
    """
    l = len(text)
    if l > 0:
        position_percent = (l - text.lower().find(word))/l
        relevance *= position_percent

    return relevance


def print_common_words_percentiles(words):

    print('UNIQUE WORDS ORDERED BY FREQUENCY')
    print('number of unique words: ' + str(len(words)))

    for percentile in range(10):
        percentile /= 10
        from_index = int(len(words) * percentile)
        to_index = int(from_index + 10)
        try:
            print('percentile {percentile}%: {words}'.format(percentile=percentile*100,
                                                             words=' '.join(words[from_index:to_index])
                                                             ))
        except UnicodeEncodeError:
            pass


def get_common_words(text_corpus, number_of_top_words=20000):
    """Gets a list of the most common words"""

    word_frequency = dict()
    for text in text_corpus.values():
        unique = set(get_word_array_lower_case_and_no_accents(text))
        unique = h.remove_accents_and_non_ascii(unique)

        for u in unique:
            if len(u) > 2 and '_' not in u:
                word_frequency[u] = word_frequency.get(u, 0) + text.count(u)

    word_frequency = [(w, f) for w, f in word_frequency.items()]
    word_frequency.sort(key=lambda x: x[1], reverse=True)

    words = [w for w, _ in word_frequency]
    words = [w for w in words if w not in cts.CONJUNCTIONS]

    print_common_words_percentiles(words)
    return words[:min(number_of_top_words, len(word_frequency))]


def empty_max(my_list):
    """
    Specially designed for ids
    :param my_list:
    :return:
    """
    if len(my_list) == 0:
        return 0
    else:
        return max(my_list)


def get_user_ids_to_update():

    try:
        last_update = pickle.load(open(cts.SEARCH_ENGINE_DATE, 'rb'))
    except FileNotFoundError:
        last_update = datetime.date(1943, 3, 13)  # very old date

    try:
        document_reader_updated_at = pickle.load(open(cts.LAST_USER_UPDATED_AT, 'rb'))
    except FileNotFoundError:
        document_reader_updated_at = datetime.date(1943, 3, 13)  # very old date

    print('starts in date: ' + str(last_update))

    # Sorts by updated at users between to updated_at intervals. The last update done and the most recent document read
    users = User.objects.filter(updated_at__gt=last_update,
                                updated_at__lt=document_reader_updated_at).order_by('updated_at').all()

    # Filter to limit number of users and reduce computation time
    users = users[:min(len(users), MAX_USERS_TO_UPDATE)]

    try:
        new_date = max([u.updated_at for u in users])
        print('ends in date: ' + str(new_date))
        pickle.dump(new_date, open(cts.SEARCH_ENGINE_DATE, 'wb'))
    except ValueError:
        pass

    return {u.id for u in users}


def save_user_relevance_dictionary():
    """
    For each word finds the user_id relevance. This is the data structure:
    word_user_dict = {
        'word_1': ((user_id_1, relevance_1), (user_id_2, relevance_2))
    }
    Returns: Saves file with dictionary
    """
    data_tf_idf, vocabulary, text_corpus = get_text_stats(use_idf=True)

    try:
        user_relevance_dictionary = pickle.load(open(cts.WORD_USER_PATH, 'rb'))
    except FileNotFoundError:
        print('FileNotFoundError: user_relevance_dictionary.p')
        print('current working directory: ' + str(os.getcwd()))
        user_relevance_dictionary = {}

    common_words = get_common_words(text_corpus)
    user_ids_to_update = get_user_ids_to_update()
    print('user_ids_to_update are: ' + str(user_ids_to_update))

    common_words = set(common_words)
    for word, num_word in vocabulary.items():

        if word in common_words:

            values = list(user_relevance_dictionary.get(word, []))
            for document, (user_id, text) in enumerate(text_corpus.items()):

                if user_id in user_ids_to_update:

                    relevance = data_tf_idf[document, num_word]

                    if relevance > 0:
                        relevance = add_position_effect(text, relevance, word)
                        values.append((int(user_id), relevance))

            user_relevance_dictionary[word] = tuple(values)

    user_relevance_dictionary = h.remove_accents_and_non_ascii(user_relevance_dictionary)

    pickle.dump(user_relevance_dictionary, open(cts.WORD_USER_PATH, 'wb'))


def run():
    sys.stdout = h.Unbuffered(open('search_engine.log', 'a'))

    h.log("STARTED RELEVANCE DICT")
    t0 = time.time()
    save_relevance_dictionary()
    t1 = time.time()
    h.log('RELEVANCE DICTIONARY, time: {}'.format(t1 - t0))

    h.log("STARTED USER RELEVANCE DICT")
    t0 = time.time()
    save_user_relevance_dictionary()
    t1 = time.time()
    h.log('USER RELEVANCE DICTIONARY, time: {}'.format(t1 - t0))


if __name__ == "__main__":
    run()
