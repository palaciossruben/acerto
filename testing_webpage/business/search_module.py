import os
import nltk
import pickle

from django.db.models import Case, When
from collections import OrderedDict

from business import util
from beta_invite.models import User
from subscribe import cts as cts_subscribe

MAX_NUM_OF_USERS = 40


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


def get_word_array_lower_case_and_no_accents(search_text):
    """
    Args:
        search_text: string
    Returns: array with words
    """
    search_text = util.remove_accents(nltk.word_tokenize(search_text))

    # remove capital letters
    return [t.lower() for t in search_text]


def filter_conjunction_words(words):
    return [w for w in words if w not in cts_subscribe.CONJUNCTIONS]


def clean_text_for_search(search_text):
    """
    Args:
        search_text: str
    Returns: List with tokenized strings, lower cased and with no accents.
    """
    words = get_word_array_lower_case_and_no_accents(search_text)
    return filter_conjunction_words(words)


def get_text_from_request(request):
    """
    Args:
        request: a Request obj
    Returns: List with tokenized strings, lower cased and with no accents.
    """
    search_text = request.GET.get('search_text')
    return clean_text_for_search(search_text)


def adds_context_based_search(tokens_dict, word_user_dictionary, filtered_user_relevance_dict):
    """
    Takes the filtered_user_relevance_dicts and modifies its relevance according to the related_words.
    Args:
        tokens_dict: List with collection of words.
        word_user_dictionary:
        filtered_user_relevance_dict:
    Returns:
    """

    # tries opening related_words_dict.p or passes by.
    try:
        # A dictionary of the form: {'word': [('related_word', relevance) ...]}
        related_words_dict = pickle.load(open(cts_subscribe.RELATED_WORDS_PATH, 'rb'))

        for t in tokens_dict.keys():
            related_words = related_words_dict.get(t, [])
            for related_word, relevance in related_words:
                user_ids = [i for i, r in word_user_dictionary.get(related_word, [])]
                for user_id, user_relevance in filtered_user_relevance_dict.items():
                    if user_id in user_ids:
                        filtered_user_relevance_dict[user_id] += relevance*user_relevance

    except FileNotFoundError:
        pass


def user_id_sorted_iterator(word_user_dictionary, users, search_phrase):
    """
    Args:
        word_user_dictionary: A dictionary of the form: {'word': (user_id, relevance)}
        users: List of User objects from previous filters.
        search_phrase: List of processed strings.
    Returns: A sorted iterator that returns tuples (user_id, relevance).
    """

    tokens_dict = {t: word_user_dictionary[t] for t in search_phrase
                   if word_user_dictionary.get(t) is not None}

    # Initializes all relevance to 0.
    user_relevance_dict = OrderedDict({user.id: 0 for user in users if user})
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


def remove_duplicates(users):
    """
    Before changes to user -> candidate, multiple users with the same email were created.
    This removes this multiple profiles.
    :param users: list of user Obj.
    :return: list of user, with unique emails.
    """
    unique_users = []
    for user in users:
        if user.email not in [u.email for u in unique_users]:
            unique_users.append(user)

    return unique_users


def get_matching_users(search_phrase):
    """
    DB matching between criteria and DB.
    Args:
        search_phrase: list of words with the text to search in.
    Returns: List with matching Users
    """

    users = User.objects.all()

    # Opens word_user_dict, or returns unordered users.
    try:
        # A dictionary of the form: {'word': (user_id, relevance)}
        word_user_dictionary = pickle.load(open(cts_subscribe.WORD_USER_PATH, 'rb'))
    except FileNotFoundError:
        return users  # will not filter by words.

    sorted_iterator = user_id_sorted_iterator(word_user_dictionary, users, search_phrase)

    users = retrieve_sorted_users(sorted_iterator)
    return remove_duplicates(users)


def get_top_matching_users(search_text):
    return get_matching_users(search_text)[:MAX_NUM_OF_USERS]


def get_common_search_info(request):
    """
    Given a Request object will do all search related stuff. Returns a maximum number of results.
    Args:
        request: HTTP object.
    Returns: profession, education, country, experience, users, user_ids
    """

    users = get_top_matching_users(get_text_from_request(request))

    util.translate_users(users, request.LANGUAGE_CODE)
    return [u.id for u in users]


# TODO: replace for ElasticSearch too!!!
def add_related_words(search_array):

    related = []
<<<<<<< Updated upstream
    try:
        # A dictionary of the form: {'word': [('related_word', relevance) ...]}
        related_words_dict = pickle.load(open(cts_subscribe.RELATED_WORDS_PATH, 'rb'))
    except FileNotFoundError:
        return []
=======

    RELATED_WORDS_PATH = os.path.join('subscribe', 'related_words_dict.p')
    my_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(my_path)
    print(os.getcwd())

    # A dictionary of the form: {'word': [('related_word', relevance) ...]}
    open(os.path.join('subscribe', 'related_words_dict.p'), encoding="utf8")
    with open(path, 'rb') as f:
        text = f.read()

    related_words_dict = pickle.load(text)
>>>>>>> Stashed changes

    for word in search_array:
        related_words = related_words_dict.get(word, [])
        print('for word {}, related:'.format(word))
        print(related_words)
        if related_words:
            related.append(related_words[0][0])

    return related
