#import sys
#sys.path.append("..")  # Adds higher directory to python modules path.
import os
import pickle
from django.core.wsgi import get_wsgi_application
from collections import OrderedDict

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

from beta_invite.models import Country, User


CONJUNCTIONS = ['las', 'para', 'los', 'del', 'and', 'el', 'en']
COUNTRIES = [e.name.lower() for e in Country.objects.all()]

nested_names = [u.name.split() for u in User.objects.all()]

# flattens list of names
NAMES = [item.lower() for sublist in nested_names for item in sublist]

PLACES = ['cauca', 'popayan', 'pereira', ]
EXCLUDED_WORDS = CONJUNCTIONS + COUNTRIES + NAMES + PLACES


def add_relevance(word, relevance, word_relevance):
    """
    Args:
        word:
        relevance:
        word_relevance:
    Returns:
    """
    if word in word_relevance:
        word_relevance[word] += relevance
    else:
        word_relevance[word] = relevance


def sort_relevance(my_dict):
    """
    Args:
        my_dict:
    Returns:
    """
    return [(w, r) for (w, r) in sorted(my_dict.items(), key=lambda x: -x[1]) if len(w) > 2]


def get_percent_relevance(user_ids, exclude_users=False):
    """
    Args:
        user_ids:
        exclude_users:
    Returns:
    """
    word_relevance = dict()
    for word, values in word_user_dictionary.items():
        for (user_id, relevance) in values:

            if exclude_users:
                if user_id not in user_ids:
                    add_relevance(word, relevance, word_relevance)
            else:
                if user_id in user_ids:
                    add_relevance(word, relevance, word_relevance)

    # TODO: stay with a 2 letter filter?
    sorted_relevance = [(w, r) for (w, r) in sorted(word_relevance.items(), key=lambda x: -x[1]) if len(w) > 2]

    total_relevance = sum([r for w, r in sorted_relevance])
    percent_relevance = [(w, r/total_relevance) for w, r in sorted_relevance]

    return OrderedDict(percent_relevance)


def get_top_related_words(user_ids, excluded_words):
    """
    Args:
        user_ids:
        excluded_words:
    Returns:
    """
    relevance_dict = get_percent_relevance(user_ids)
    excluded_relevance_dict = get_percent_relevance(user_ids, exclude_users=True)

    subtracted_dict = OrderedDict()
    for word, relevance in relevance_dict.items():
        if word not in excluded_words:
            subtracted_dict[word] = relevance - excluded_relevance_dict.get(word, 0)

    return sort_relevance(subtracted_dict)[:10]


# A dictionary of the form: {'word': (user_id, relevance)}
word_user_dictionary = pickle.load(open('../subscribe/word_user_dictionary.p', 'rb'))

relevance_dictionary = pickle.load(open('relevance_dictionary.p', 'rb'))

#print([(w, r) for w, r in sorted(relevance_dictionary.items(), key=lambda x: -x[1])])

top_related_words_dict = dict()
for keyword, values in word_user_dictionary.items():

    if keyword not in EXCLUDED_WORDS:
        user_ids = [i for (i, r) in values]

        sorted_final = get_top_related_words(user_ids, EXCLUDED_WORDS + [keyword])

        #print(keyword)
        #print(sorted_final)

        top_related_words_dict[keyword[0]] = sorted_final


pickle.dump(top_related_words_dict, open('top_related_words_dict.p', 'wb'))
