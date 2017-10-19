import nltk
import pickle

from django.db.models import Case, When
from collections import OrderedDict
from business import util
from beta_invite.models import User, Country, Education, Profession

MAX_NUM_OF_USERS = 20


def filter_relevance_users(user_relevance_dict):
    """
    Filters for users who have zero relevance.
    Args:
        user_relevance_dict: A dictionary of the form: {user_id: relevance ...}
        Gives the relevance of a word for a specific user.
    Returns: filtered users.
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


def adds_context_based_search(tokens_dict, word_user_dictionary, filtered_user_relevance_dict):
    """
    Takes the filtered_user_relevance_dicts and modifies its relevance according to the top_related_words.
    Args:
        tokens_dict: List with collection of words.
        word_user_dictionary:
        filtered_user_relevance_dict:
    Returns:
    """

    # tries opening top_related_words_dict.p or passes by.
    try:
        # A dictionary of the form: {'word': [('related_word', relevance) ...]}
        top_related_words = pickle.load(open('subscribe/top_related_words_dict.p', 'rb'))

        for t in tokens_dict.keys():
            related_words = top_related_words.get(t, [])
            for related_word, relevance in related_words:
                user_ids = [i for i, r in word_user_dictionary.get(related_word, [])]
                for user_id, user_relevance in filtered_user_relevance_dict.items():
                    if user_id in user_ids:
                        filtered_user_relevance_dict[user_id] += relevance*user_relevance

    except FileNotFoundError:
        pass


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

    filtered_user_relevance_dict = filter_relevance_users(user_relevance_dict)

    adds_context_based_search(tokens_dict, word_user_dictionary, filtered_user_relevance_dict)

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


def get_matching_users2(search_text, word_user_path):
    """
    DB matching between criteria and DB.
    Args:
        search_text: string with the text to search in
        word_user_path: string with path to the object.
    Returns: List with matching Users
    """

    users = User.objects.all()

    # Opens word_user_dict, or returns unordered users.
    try:
        # A dictionary of the form: {'word': (user_id, relevance)}
        word_user_dictionary = pickle.load(open(word_user_path, 'rb'))
    except FileNotFoundError:
        return users  # will not filter by words.

    sorted_iterator = user_id_sorted_iterator2(word_user_dictionary, users, search_text)

    #print_sorted_iterator_on_debug(sorted_iterator)

    return retrieve_sorted_users(sorted_iterator)


def get_common_search_info2(request, word_user_path):
    """
    Given a Request object will do all search related stuff. Returns a maximum number of results.
    Args:
        request: HTTP object.
        word_user_path: string with path of object
    Returns: profession, education, country, experience, users, user_ids
    """

    users = get_matching_users2(get_text(request), word_user_path)
    users = users[:MAX_NUM_OF_USERS]

    util.translate_users(users, request.LANGUAGE_CODE)
    return [u.id for u in users]

