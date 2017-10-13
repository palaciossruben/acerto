import nltk
import pickle

from django.db.models import Case, When
from collections import OrderedDict
from business import util
from beta_invite.models import User, Country, Education, Profession


def filter_zero_relevance_users(user_relevance_dict):
    """
    Filters for users who have zero relevance.
    Args:
        user_relevance_dict: A dictionary of the form: {user_id: relevance ...}
        Gives the relevance of a word for a specific user.
    Returns:

    """

    filtered_user_relevance_dict = OrderedDict()
    for user_id, relevance in user_relevance_dict.items():
        if relevance > 0:
            filtered_user_relevance_dict[user_id] = relevance

    return filtered_user_relevance_dict


def get_text(request):
    """
    Args:
        request: a Request obj
    Returns: List with tokenized strings, lower cased and with no accents.
    """
    search_text = request.GET.get('search_text')
    search_text = util.remove_accents(nltk.word_tokenize(search_text))

    # remove capital letters
    return [t.lower() for t in search_text]


def user_id_sorted_iterator2(word_user_dictionary, users, skills):
    """
    Args:
        word_user_dictionary: A dictionary of the form: {'word': (user_id, relevance)}
        users: List of User objects from previous filters.
        skills: List of processed strings.
    Returns: A sorted iterator that returns tuples (user_id, relevance).
    """
    tokens_dict = {t: word_user_dictionary[t] for t in skills
                   if word_user_dictionary.get(t) is not None}

    # Initializes all relevance to 0.
    user_relevance_dict = OrderedDict({user.id: 0 for user in users})
    for k, values in tokens_dict.items():
        for value_user_id, relevance in values:

            if value_user_id in user_relevance_dict.keys():
                user_relevance_dict[value_user_id] += relevance

    filtered_user_relevance_dict = filter_zero_relevance_users(user_relevance_dict)

    # Sorts by DESC relevance.
    return reversed(sorted(filtered_user_relevance_dict.items(), key=lambda x: x[1]))


def retrieve_sorted_users(sorted_iterator):
    """
    An iterable object that outputs the sorted tuples (user_ids, relevance)
    Args:
        sorted_iterator: Iterable object.
    Returns: Sorted User objects Query Set.
    """
    user_ids = [user_id[0] for user_id in sorted_iterator]

    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(user_ids)])
    return User.objects.filter(pk__in=user_ids).order_by(preserved)


def get_matching_users2(request):
    """
    DB matching between criteria and DB.
    Args:
        request: Request obj
    Returns: List with matching Users
    """

    users = User.objects.all()

    # Opens word_user_dict, or returns unordered users.
    try:
        # A dictionary of the form: {'word': (user_id, relevance)}
        word_user_dictionary = pickle.load(open('subscribe/word_user_dictionary.p', 'rb'))
    except FileNotFoundError:
        return users  # will not filter by words.

    sorted_iterator = user_id_sorted_iterator2(word_user_dictionary, users, get_text(request))

    #print_sorted_iterator_on_debug(sorted_iterator)

    return retrieve_sorted_users(sorted_iterator)


def get_common_search_info2(request):
    """
    Given a Request object will do all search related stuff
    Args:
        request: HTTP object.
    Returns: profession, education, country, experience, users, user_ids
    """

    users = get_matching_users2(request)
    util.translate_users(users, request.LANGUAGE_CODE)
    return [u.id for u in users]

