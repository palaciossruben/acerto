import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.testing_webpage.settings')
application = get_wsgi_application()

import nltk
import pickle
import smtplib
import unicodedata

from django.contrib.auth.decorators import login_required
from collections import OrderedDict
from ipware.ip import get_ip
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from django.db.models import Case, When
from django.contrib.auth import login, authenticate

import business
import beta_invite
from beta_invite.util import email_sender
from business import constants as cts
from beta_invite.models import User, Country, Education, Profession
from business.models import Plan, Offer, Contact, Search
from business.models import User as BusinessUser
from business.custom_user_creation_form import CustomUserCreationForm


def index(request):
    """
    will render and have the same view as /beta_invite except for message customization.
    Args:
        request: Object
    Returns: Save
    """

    ip = get_ip(request)
    action_url = '/business/post'

    secondary_message = _("We do the entire personnel selection process for your company.")

    business.models.Visitor(ip=ip, ui_version=cts.UI_VERSION).save()
    return render(request, cts.BUSINESS_VIEW_PATH, {'main_message': _("Discover amazing people"),
                                                    'secondary_message': secondary_message,
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

    return render(request, cts.POST_JOB_VIEW_PATH, {'main_message': _("Discover amazing people"),
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


def search_trade(request):
    """
    will render the search view.
    Args:
        request: Object
    Returns: Save
    """

    ip = get_ip(request)
    action_url = '/business/trade_results'
    countries, trades = beta_invite.views.get_trade_drop_down_values(request.LANGUAGE_CODE)

    business.models.Visitor(ip=ip, ui_version=cts.UI_VERSION).save()
    return render(request, cts.SEARCH_VIEW_PATH, {'action_url': action_url,
                                                  'countries': countries,
                                                  'trades': trades,
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


def calculate_result(request):
    """
    Args:
        request: Request object
    Returns: renders results.html view.
    """

    profession, education, country, experience, users, user_ids = get_common_search_info(request)

    search_obj = Search(ip=get_ip(request),
                        country=country,
                        education=education,
                        profession=profession,
                        experience=experience,
                        skills=get_skills(request),
                        user_ids=user_ids,)

    search_obj.save()

    return redirect('results/{id}'.format(id=search_obj.id))


def render_result(request, pk):
    """
    Gets a stored search back to life.
    Args:
        request: HTTP request.
        pk: primary key of a search
    Returns: Renders search results.
    """

    search_obj = Search.objects.get(pk=pk)
    users = [User.objects.get(pk=u_id) for u_id in search_obj.user_ids]

    return render(request, cts.RESULTS_VIEW_PATH, {'main_message': _("Discover amazing people"),
                                                   'secondary_message': _("We search millions of profiles and find the ones that best suit your business"),
                                                   'users': users,
                                                   })


def offer_detail(request):
    """
    Args:
        request: HTTP request.
    Returns: renders the detailed view of a given offer
    """
    offer_id = request.GET.get('id', None)

    if offer_id is not None:

        offer = Offer.objects.get(pk=offer_id)
        users = [User.objects.get(pk=u_id) for u_id in offer.user_ids]
        translate_users(users, request.LANGUAGE_CODE)

        return render(request, cts.OFFER_RESULTS_VIEW_PATH, {'users': users,
                                                             })

    else:  # reloads home, if nothing found
        home(request)


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


# TODO: print any error messages when trying to login.
def signup(request):
    """
    Args:
        request: HTTP post request
    Returns: Renders form.html.
    """
    plan_name = request.POST.get('plan_name')
    try:
        plan = Plan.objects.get(name=plan_name)
    except:
        # If no plan object found will, use a default message
        plan = Plan.objects.get(name='Default')

    plan = translate_message(plan, request.LANGUAGE_CODE)

    return render(request, cts.SIGNUP_VIEW_PATH, {'main_message': plan.message,
                                                  'plan_id': plan.id})


def get_plan(request):
    """
    Args:
        request: HTTP request
    Returns: Returns a Plan obj
    """

    plan_id = request.POST.get('plan_id')
    try:
        plan = Plan.objects.get(pk=plan_id)
    except:
        # Gets the default plan.
        plan = Plan.objects.get(pk=4)

    return translate_message(plan, request.LANGUAGE_CODE)


def first_sign_in(signup_form, request):
    """
    This method is used to do stuff after validating signup-data. Also logs in.
    Args:
        signup_form: Form obj
        request: HTTP obj
    Returns: None, first auth and sign-in, saves objects
    """

    plan = get_plan(request)

    signup_form.save()
    username = signup_form.cleaned_data.get('username')
    password = signup_form.cleaned_data.get('password1')

    # Creates a Authentication user
    auth_user = authenticate(username=username,
                             password=password)

    # New BusinessUser pointing to the AuthUser
    business.models.User(name=request.POST.get('name'),
                         email=request.POST.get('username'),
                         phone=request.POST.get('phone'),
                         ip=get_ip(request),
                         ui_version=cts.UI_VERSION,
                         plan=plan,
                         auth_user_id=auth_user.id).save()

    login(request, auth_user)


def post_first_job(request):
    """
    Args:
        request: HTTP post request
    Returns: Renders form.html.
    """

    signup_form = CustomUserCreationForm(request.POST)

    if signup_form.is_valid():

        first_sign_in(signup_form, request)
        countries, education, professions = beta_invite.views.get_drop_down_values(request.LANGUAGE_CODE)
        return render(request, cts.POST_JOB_VIEW_PATH, {'countries': countries,
                                                        'education': education,
                                                        'professions': professions,
                                                        'is_new_user': True,
                                                        })
    else:

        # Takes first element from the errors dictionary
        error_message = [m[0] for m in signup_form.errors.values()][0]
        plan = get_plan(request)

        return render(request, cts.SIGNUP_VIEW_PATH, {'main_message': plan.message,
                                                      'plan_id': plan.id,
                                                      'error_message': error_message})


def popup_signup(request):
    """
    Args:
        request: HTTP obj
    Returns: Redirects.
    """

    signup_form = CustomUserCreationForm(request.POST)

    if signup_form.is_valid():
        first_sign_in(signup_form, request)
        return redirect('business:search')
    else:

        # Takes first element from the errors dictionary
        error_message = [m[0] for m in signup_form.errors.values()][0]

        countries, education, professions = beta_invite.views.get_drop_down_values(request.LANGUAGE_CODE)
        action_url = '/business/results'

        return render(request, cts.SEARCH_VIEW_PATH, {'main_message': _("Discover amazing people"),
                                                      'secondary_message': _("We search millions of profiles and find the ones that best suit your business"),
                                                      'action_url': action_url,
                                                      'countries': countries,
                                                      'education': education,
                                                      'professions': professions,
                                                      'error_message': error_message,
                                                      })


@login_required
def post_job(request):
    """
    Creates the view for posting new job offers.
    Args:
        request: HTTP request object.
    Returns: renders view.
    """

    countries, education, professions = beta_invite.views.get_drop_down_values(request.LANGUAGE_CODE)

    return render(request, cts.POST_JOB_VIEW_PATH, {'countries': countries,
                                                    'education': education,
                                                    'professions': professions,
                                                    'is_new_user': False,
                                                    })


def get_business_user(request):
    """
    Given a request that has the AuthUser.id will get the BusinessUser
    Args:
        request: HTTP request object.
    Returns: A BusinessUser object.
    """

    auth_user_id = request.user.id
    business_user = BusinessUser.objects.get(auth_user_id=auth_user_id)

    return business_user


def get_common_search_info(request):
    """
    Given a Request object will do all search related stuff
    Args:
        request: HTTP object.
    Returns: profession, education, country, experience, users, user_ids
    """

    profession_id = request.POST.get('profession')
    profession = Profession.objects.get(pk=profession_id)
    education_id = request.POST.get('education')
    education = Education.objects.get(pk=education_id)

    country_id = request.POST.get('country')
    country = Country.objects.get(pk=country_id)
    experience = request.POST.get('experience')

    users = get_matching_users(request)
    translate_users(users, request.LANGUAGE_CODE)

    user_ids = [u.id for u in users]

    return profession, education, country, experience, users, user_ids


@login_required
def offer_results(request):
    """
    Will save and show the partial results of a job offer.
    Args:
        request: HTTP object.
    Returns: Save and render results
    """

    profession, education, country, experience, users, user_ids = get_common_search_info(request)

    Offer(business_user=get_business_user(request),
          country=country,
          education=education,
          profession=profession,
          experience=experience,
          skills=get_skills(request),
          user_ids=user_ids,).save()

    return render(request, cts.OFFER_RESULTS_VIEW_PATH, {'users': users,
                                                         })


@login_required
def home(request):
    """
    Dashboard View. It displays all offers of a
    Args:
        request: HTTP request.
    Returns: displays all offers of a business
    """

    offers = Offer.objects.filter(business_user_id=get_business_user(request))
    return render(request, cts.HOME_VIEW_PATH, {'offers': offers,
                                                })


def send_contact_emails(contact, language_code):

    try:
        email_sender.send(user=contact,
                          language_code=language_code,
                          body_filename='business_contact_email_body',
                          subject=_('Welcome to PeakU'))
        email_sender.send_internal(contact=contact,
                                   language_code=language_code,
                                   body_filename='contact_notification_email_body',
                                   subject='Business User acaba de llenar formulario de contacto!!!')
    except (smtplib.SMTPRecipientsRefused, smtplib.SMTPAuthenticationError, UnicodeEncodeError) as e:  # cannot send emails
        pass


def contact_us(request):
    """
    Save a comment from the contact form
    Args:
        request: HTTP obj
    Returns: render a thanks page
    """
    contact = Contact(name=request.POST.get('name'),
                      email=request.POST.get('email'),
                      phone=request.POST.get('phone'),
                      message=request.POST.get('message'),)

    contact.save()

    send_contact_emails(contact, request.LANGUAGE_CODE)

    # TODO: make this shit work
    # Send emails without blocking
    #loop = asyncio.get_event_loop()
    #loop.run_until_complete(send_contact_emails(contact, request.LANGUAGE_CODE))
    #loop.close()

    return render(request, cts.CONTACT_VIEW_PATH, {'main_message': _("Discover amazing people"),})


def translate_plan(plan_obj, language_code):
    """
    Args:
        plan_obj: an obj Plan
        language_code: can be 'es'
    Returns: translated obj
    """
    if 'es' in language_code:
        plan_obj.explanation = plan_obj.explanation_es
        plan_obj.name = plan_obj.name_es

    return plan_obj


def plan(request, pk):
    """
    Args:
        request: HTTP request
        pk: primary key of the Plan object.
    Returns: Renders the plan detailed explanation
    """
    plan_obj = Plan.objects.get(pk=pk)
    plan_obj = translate_plan(plan_obj, request.LANGUAGE_CODE)

    return render(request, cts.PLAN_VIEW_PATH, {'plan': plan_obj})


def trade_client(request):
    """
    will render and have the same view as /beta_invite except for message customization.
    Args:
        request: Object
    Returns: Save
    """

    ip = get_ip(request)
    action_url = '/business/post'

    secondary_message = _("Find someone to help you with daily tasks such as cleaning your house, fixing the fridge or sending a message.")

    business.models.Visitor(ip=ip, ui_version=cts.UI_VERSION).save()
    return render(request, cts.TRADE_CLIENT_VIEW_PATH, {'main_message': _("Solve everyday problems"),
                                                        'secondary_message': secondary_message,
                                                        'action_url': action_url,
                                                        })
