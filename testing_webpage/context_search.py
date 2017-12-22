"""
Builds a dictionary(top_related_words_dict.p) of the form: {'word':[('related_word', relevance) ...]}
The list only contains the top 10 more closely connected words.
This builds a relationship between words for example 'android' has the following connections:
[('aplicaciones', 0.0059724685930693444), ('web', 0.0048486894726525584), ('software', 0.0039564690292684512), ...
"""

import os
import time
import pickle
from django.core.wsgi import get_wsgi_application
from collections import OrderedDict

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

from beta_invite.models import Country, User


CONJUNCTIONS = {'las', 'para', 'los', 'del', 'and', 'el', 'en'}
COUNTRIES = {e.name.lower() for e in Country.objects.all()}

nested_names = [u.name.split() for u in User.objects.all()]

# flattens list of names
NAMES = {item.lower() for sublist in nested_names for item in sublist}

PLACES = {'cauca', 'popayan', 'pereira', }
EXCLUDED_WORDS = CONJUNCTIONS | COUNTRIES | NAMES | PLACES


def sort_relevance(my_dict):
    """
    Sorts dictionary by value
    Args:
        my_dict: dictionary where values can are relevance floats.
    Returns: Sorted array with tuples
    """
    return [(w, r) for (w, r) in sorted(my_dict.items(), key=lambda x: -x[1]) if len(w) > 2]


def get_percent_dict(word_relevance):
    """
    From a dictionary with absolute relevance gets the percent relevance.
    Args:
        word_relevance: dict with {'word': relevance}
    Returns: OrderedDict with {'word': percent_relevance}
    """

    total_relevance = sum([r for w, r in word_relevance.items()])
    percent_relevance = [(w, r/total_relevance) for w, r in word_relevance.items()]

    return OrderedDict(percent_relevance)


def get_percent_relevance(word_user_dictionary, user_ids, excluded_words):
    """
    Args:
        word_user_dictionary: of the form: {'word': (user_id, relevance) ...}
        user_ids: set with all the user ids.
        excluded_words: set of excluded words.
    Returns:
    """
    word_relevance = dict()
    excluded_relevance = dict()
    for word, values in word_user_dictionary.items():

        if word not in excluded_words:

            for (user_id, relevance) in values:

                if user_id not in user_ids:
                    excluded_relevance[word] = excluded_relevance.get(word, 0) + relevance
                else:
                    word_relevance[word] = word_relevance.get(word, 0) + relevance

    relevance_dict, excluded_relevance_dict = get_percent_dict(word_relevance), get_percent_dict(excluded_relevance)

    subtracted_dict = OrderedDict()
    for word, relevance in relevance_dict.items():
        if word not in excluded_words:
            subtracted_dict[word] = relevance - excluded_relevance_dict.get(word, 0)

    return subtracted_dict


def get_top_related_words(word_user_dictionary, user_ids, excluded_words):
    """
    Args:
        word_user_dictionary: of the form: {'word': (user_id, relevance) ...}
        user_ids: set of ids.
        excluded_words: set of excluded words.
    Returns: The top 10 related words, sorted by DESC relevance
    """
    subtracted_dict = get_percent_relevance(word_user_dictionary, user_ids, excluded_words)
    return sort_relevance(subtracted_dict)[:10]


def compute_related_words():
    """
    Returns: None, stores top_related_words_dict.p dictionary of the form: {'word': ('related_word', relevance) ...}
    """

    # A dictionary of the form: {'word': (user_id, relevance)}
    word_user_dictionary = pickle.load(open('../subscribe/word_user_dictionary.p', 'rb'))

    top_related_words_dict = dict()
    for keyword, values in word_user_dictionary.items():

        if keyword not in EXCLUDED_WORDS:
            user_ids = {i for (i, r) in values}

            sorted_final = get_top_related_words(word_user_dictionary, user_ids, EXCLUDED_WORDS | {keyword})

            top_related_words_dict[keyword] = sorted_final

    pickle.dump(top_related_words_dict, open('top_related_words_dict.p', 'wb'))


if __name__ == '__main__':

    t0 = time.time()
    # TODO: Get relevances with word2vec and gensim.
    compute_related_words()
    t1 = time.time()
    print('CONTEXT SEARCH TOOK: ' + str(t1-t0))
