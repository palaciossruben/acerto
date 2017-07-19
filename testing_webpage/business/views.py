import nltk
import pickle
import unicodedata

from collections import OrderedDict
from ipware.ip import get_ip
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.db.models import Case, When

import business
import beta_invite
from business import constants as cts
from beta_invite.models import User, Education
from business.models import Plan


def index(request):
    """
    will render and have the same view as /beta_invite except for message customization.
    Args:
        request: Object
    Returns: Save
    """

    ip = get_ip(request)
    action_url = '/business/post'

    business.models.Visitor(ip=ip, ui_version=cts.UI_VERSION).save()
    return render(request, cts.BUSINESS_VIEW_PATH, {'main_message': _("Discover amazing people"),
                                                    'secondary_message': _("We search millions of profiles and find the ones that best suit your business"),
                                                    'action_url': action_url,
                                                    })


def post_index(request):
    """
    Saves model to DB
    Args:
        request:

    Returns: Saves
    """
    ip = get_ip(request)
    business_user = business.models.User(name=request.POST.get('name'),
                                         email=request.POST.get('email'),
                                         ip=ip,
                                         ui_version=cts.UI_VERSION)
    business_user.save()

    # TODO: pay the monthly fee
    #try:
    #    email_sender.send(user, request.LANGUAGE_CODE)
    #except smtplib.SMTPRecipientsRefused:  # cannot send, possibly invalid emails
    #    pass

    return render(request, cts.SUCCESS_VIEW_PATH, {'main_message': _("Discover amazing people"),
                                                   'secondary_message': _("We search millions of profiles and find the ones that best suit your business"),
                                                   })


def search(request):
    """
    will render the search view.
    Args:
        request: Object
    Returns: Save
    """

    ip = get_ip(request)
    action_url = '/business/results'

    countries, education, professions = beta_invite.views.get_drop_down_values(request.LANGUAGE_CODE)

    business.models.Visitor(ip=ip, ui_version=cts.UI_VERSION).save()
    return render(request, cts.SEARCH_VIEW_PATH, {'main_message': _("Discover amazing people"),
                                                  'secondary_message': _("We search millions of profiles and find the ones that best suit your business"),
                                                  'action_url': action_url,
                                                  'countries': countries,
                                                  'education': education,
                                                  'professions': professions,
                                                  })


# TODO: duplicate code: see subscribe.helper
def remove_accents_in_string(element):
    """
    Args:
        element: anything.
    Returns: Cleans accents only for strings.
    """
    if isinstance(element, str):
        return ''.join(c for c in unicodedata.normalize('NFD', element) if unicodedata.category(c) != 'Mn')
    else:
        return element


# TODO: duplicate code: see subscribe.helper
def remove_accents(an_object):
    """
    Several different objects can be cleaned.
    Args:
        an_object: can be list, string, tuple and dict
    Returns: the cleaned obj, or a exception if not implemented.
    """
    if isinstance(an_object, str):
        return remove_accents_in_string(an_object)
    elif isinstance(an_object, list):
        return [remove_accents_in_string(e) for e in an_object]
    elif isinstance(an_object, tuple):
        return tuple([remove_accents_in_string(e) for e in an_object])
    elif isinstance(an_object, dict):
        return {remove_accents_in_string(k): remove_accents_in_string(v) for k, v in an_object.items()}
    else:
        raise NotImplementedError


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


def get_skills(request):
    """
    Args:
        request: a Request obj
    Returns: List with tokenized strings, lower cased and with no accents.
    """
    skills = request.POST.get('skills')
    skills = remove_accents(nltk.word_tokenize(skills))

    # remove capital letters
    return [t.lower() for t in skills]


def user_id_sorted_iterator(user_relevance_dictionary, users, skills):
    """
    Args:
        user_relevance_dictionary: Vocabulary and relevance dict.
        users: List of User objects from previous filters.
        skills: List of processed strings.
    Returns: A sorted iterator that returns tuples (user_id, relevance).
    """
    tokens_dict = {t: user_relevance_dictionary[t] for t in skills
                   if user_relevance_dictionary.get(t) is not None}

    # Initializes all relevance to 0.
    user_relevance_dict = OrderedDict({user.id: 0 for user in users})
    for k, values in tokens_dict.items():
        for value_user_id, relevance in values:

            if value_user_id in user_relevance_dict.keys():
                user_relevance_dict[value_user_id] += relevance

    return reversed(sorted(user_relevance_dict.items(), key=lambda x: x[1]))


def print_sorted_iterator_on_debug(sorted_iterator):
    import copy
    sorted_2 = copy.copy(sorted_iterator)

    print('SORTED ITERATOR IS:')
    for i in sorted_2:
        print(i)


def get_matching_users(request):
    """
    DB matching between criteria and DB.
    Args:
        request: Request obj
    Returns: List with matching Users
    """

    profession_id = request.POST.get('profession')
    education_id = request.POST.get('education')
    education_level = Education.objects.get(pk=education_id)

    # Get all education levels at or above the object.
    education_set = Education.objects.filter(level__gte=education_level.level)

    country_id = request.POST.get('country')
    experience = request.POST.get('experience')

    users = User.objects.filter(country_id=country_id)\
        .filter(profession_id=profession_id)\
        .filter(experience__gte=experience)\
        .filter(education__in=education_set)

    # Opens word_user_dict, or returns unordered users.
    try:
        user_relevance_dictionary = pickle.load(open('subscribe/user_relevance_dictionary.p', 'rb'))
    except FileNotFoundError:
        return users  # will not filter by words.

    sorted_iterator = user_id_sorted_iterator(user_relevance_dictionary, users, get_skills(request))

    #print_sorted_iterator_on_debug(sorted_iterator)

    return retrieve_sorted_users(sorted_iterator)


def translate_users(users, language_code):
    """
    Args:
        users: List of Users
        language_code: can be 'es'
    Returns: List of translated users
    """
    if 'es' in language_code:
        for u in users:
            u.profession.name = u.profession.name_es
            u.education.name = u.education.name_es


def results(request):
    """
    Args:
        request: Request object
    Returns: renders results.html view.
    """

    users = get_matching_users(request)

    translate_users(users, request.LANGUAGE_CODE)

    return render(request, cts.RESULTS_VIEW_PATH, {'main_message': _("Discover amazing people"),
                                                   'secondary_message': _("We search millions of profiles and find the ones that best suit your business"),
                                                   'users': users,
                                                   })


def translate_message(plan, language_code):
    """
    Args:
        plan: Object of class Plan.
        language_code:
    Returns:
    """
    if 'es' in language_code:
        plan.message = plan.message_es

    return plan


def form(request):
    """
    Args:
        request: HTTP post request
    Returns: Renders form.html.
    """
    plan_name = request.POST.get('plan_name')
    plan = Plan.objects.get(name=plan_name)
    plan = translate_message(plan, request.LANGUAGE_CODE)

    return render(request, cts.FORM_VIEW_PATH, {'main_message': plan.message,
                                                'plan_id': plan.id})


def form_post(request):
    """
    Args:
        request: HTTP post request
    Returns: Renders form.html.
    """
    plan_id = request.POST.get('plan_id')
    plan = Plan.objects.get(pk=plan_id)

    ip = get_ip(request)
    business_user = business.models.User(name=request.POST.get('name'),
                                         email=request.POST.get('email'),
                                         ip=ip,
                                         ui_version=cts.UI_VERSION,
                                         plan=plan)
    business_user.save()

    return render(request, cts.SUCCESS_VIEW_PATH, {'main_message': _("Discover amazing people"),
                                                   'secondary_message': _("We search millions of profiles and find the ones that best suit your business"),
                                                   })
