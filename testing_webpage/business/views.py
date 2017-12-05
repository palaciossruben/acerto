import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.testing_webpage.settings')
application = get_wsgi_application()

import pickle
import smtplib

from django.contrib.auth.decorators import login_required
from collections import OrderedDict
from ipware.ip import get_ip
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import login, authenticate
from django.core.exceptions import ObjectDoesNotExist

import business
import beta_invite
from business import util
from business import search_module
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

    business.models.Visitor(ip=ip, ui_version=cts.UI_VERSION).save()
    return render(request, cts.BUSINESS_VIEW_PATH, {})


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
                                                  'error_message': None,
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

    # Sorts by DESC relevance.
    return reversed(sorted(user_relevance_dict.items(), key=lambda x: x[1]))


def get_filtered_users(country_id, profession_id, experience, education_id):
    """
    Filters users given certain conditions.
    Args:
        country_id: int
        profession_id: int
        experience: int
        education_id: int
    Returns:
    """
    # Get all education levels at or above.
    education_level = Education.objects.get(pk=education_id)
    education_set = Education.objects.filter(level__gte=education_level.level)

    return User.objects.filter(country_id=country_id)\
        .filter(profession_id=profession_id)\
        .filter(experience__gte=experience)\
        .filter(education__in=education_set)


def get_matching_users(request):
    """
    DB matching between criteria and DB.
    Args:
        request: Request obj
    Returns: List with matching Users
    """

    profession_id = request.POST.get('profession')
    education_id = request.POST.get('education')

    country_id = request.POST.get('country')
    experience = request.POST.get('experience')

    users = get_filtered_users(country_id, profession_id, experience, education_id)

    # Opens word_user_dict, or returns unordered users.
    try:
        user_relevance_dictionary = pickle.load(open('subscribe/user_relevance_dictionary.p', 'rb'))
    except FileNotFoundError:
        return users  # will not filter by words.

    sorted_iterator = user_id_sorted_iterator(user_relevance_dictionary, users, search_module.get_text(request))

    return search_module.retrieve_sorted_users(sorted_iterator)


def calculate_result2(request):
    """
    Args:
        request: Request object
    Returns: renders results.html view.
    """

    user_ids = search_module.get_common_search_info2(request, 'subscribe/word_user_dictionary.p')

    search_obj = Search(ip=get_ip(request),
                        country=None,
                        education=None,
                        profession=None,
                        experience=None,
                        skills=search_module.get_text(request),
                        user_ids=user_ids, )

    search_obj.save()

    return redirect('results/{id}'.format(id=search_obj.id))


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
                        skills=search_module.get_text(request),
                        user_ids=user_ids, )

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
    params = {'main_message': _("Discover amazing people"),
              'secondary_message': _("We search millions of profiles and find the ones that best suit your business"),
              'users': users}

    if hasattr(request, 'error_message') and request.error_message is not None:
        params['error_message'] = request.error_message

    return render(request, cts.RESULTS_VIEW_PATH, params)


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
        util.translate_users(users, request.LANGUAGE_CODE)

        return render(request, cts.OFFER_RESULTS_VIEW_PATH, {'users': users})

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
    except :
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
    except ObjectDoesNotExist:
        # Gets the default plan.
        plan = Plan.objects.get(pk=4)

    return translate_message(plan, request.LANGUAGE_CODE)


def send_signup_emails(business_user, language_code):

    try:
        email_sender.send(users=business_user,
                          language_code=language_code,
                          body_input='business_signup_email_body',
                          subject=_('Welcome to PeakU'))
        email_sender.send_internal(contact=business_user,
                                   language_code=language_code,
                                   body_filename='business_signup_notification_email_body',
                                   subject='Business User acaba de registrarse!!!')
    except (smtplib.SMTPRecipientsRefused, smtplib.SMTPAuthenticationError, UnicodeEncodeError) as e:  # cannot send emails
        pass


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
    business_user = business.models.User(name=request.POST.get('name'),
                                         email=request.POST.get('username'),
                                         phone=request.POST.get('phone'),
                                         ip=get_ip(request),
                                         ui_version=cts.UI_VERSION,
                                         plan=plan,
                                         auth_user_id=auth_user.id)

    business_user.save()

    login(request, auth_user)

    send_signup_emails(business_user, request.LANGUAGE_CODE)


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
        return redirect(request.POST.get('result_path'))
    else:
        error_message = [m[0] for m in signup_form.errors.values()][0]
        request.error_message = error_message

        path = request.POST.get('result_path')
        if path is not None:
            # last part of url is result_id
            result_id = int(path.split('/')[-1])
            return render_result(request, result_id)
        else:
            # Defensive programming: not the best, but better than an error.
            # We have lost the result_id
            return redirect('business:search')


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
    util.translate_users(users, request.LANGUAGE_CODE)

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
          skills=search_module.get_text(request),
          user_ids=user_ids, ).save()

    return render(request, cts.OFFER_RESULTS_VIEW_PATH, {'users': users})


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

    return render(request, cts.CONTACT_VIEW_PATH, {'main_message': _("Discover amazing people"), })


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
        plan_obj.interview_price = plan_obj.interview_price_es
        plan_obj.contract_warranty = plan_obj.contract_warranty_es

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
