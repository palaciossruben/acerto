import nltk
import pickle
import unicodedata

from collections import OrderedDict
from ipware.ip import get_ip
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

import business
import beta_invite
from business import constants as cts
from beta_invite.models import User, Education


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


def get_matching_users(request):
    """
    Simple DB matching between criteria and DB.
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

    skills = request.POST.get('skills')
    tokenized_skills = remove_accents(nltk.word_tokenize(skills))

    # Opens word_user_dict
    vocabulary_user_dict = pickle.load(open('subscribe/vocabulary_user_dict.p', 'rb'))
    tokens_dict = {t: vocabulary_user_dict[t] for t in tokenized_skills if vocabulary_user_dict.get(t) is not None}

    users = User.objects.filter(country_id=country_id)\
        .filter(profession_id=profession_id)\
        .filter(experience__gte=experience)\
        .filter(education__in=education_set)

    # Initializes all relevance in 0.

    user_relevance_dict = OrderedDict({user.id: 0 for user in users})
    for k, values in tokens_dict.items():
        for value_user_id, relevance in values:

            if value_user_id in user_relevance_dict.keys():
                # if there is no score yet, then assigns the relevance, else sums the relevance.
                user_relevance_dict[value_user_id] += relevance

    sorted_iterator = reversed(sorted(user_relevance_dict.items(), key=lambda x: x[1]))

    # Only one query set with all objects.
    users = User.objects.filter(pk__in=[user_id for user_id, _ in sorted_iterator])
    return users


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
