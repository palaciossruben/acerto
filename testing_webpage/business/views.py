import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.testing_webpage.settings')
application = get_wsgi_application()

import smtplib

from django.contrib.auth.decorators import login_required
from ipware.ip import get_ip
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import login, authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.forms import AuthenticationForm

import common
import business
import beta_invite
from business import search_module
from beta_invite.util import email_sender
from business import constants as cts
from beta_invite.models import User, BulletType, WorkArea, EmailType, Campaign
from business.models import Plan, Contact, Search
from business.models import BusinessUser
from business.custom_user_creation_form import CustomUserCreationForm
from dashboard import campaign_module
from dashboard.models import Candidate
from business import dashboard_module
from testing_webpage.models import BusinessUserPendingEmail


def index(request):
    """
    will render and have the same view as /beta_invite except for message customization.
    Args:
        request: Object
    Returns: Save
    """

    ip = get_ip(request)

    business.models.Visitor(ip=ip).save()
    return render(request, cts.INDEX_VIEW_PATH, {'error_message': ''})


def search(request):
    """
    will render the search view.
    Args:
        request: Object
    Returns: Save
    """

    ip = get_ip(request)
    action_url = '/business/results'
    countries, cities, education, professions = beta_invite.views.get_drop_down_values(request.LANGUAGE_CODE)

    business.models.Visitor(ip=ip).save()
    return render(request, cts.SEARCH_VIEW_PATH, {'main_message': _("Discover amazing people"),
                                                  'secondary_message': _("We search millions of profiles and find the ones that best suit your business"),
                                                  'action_url': action_url,
                                                  'countries': countries,
                                                  'education': education,
                                                  'professions': professions,
                                                  })


def calculate_result(request):
    """
    Args:
        request: Request object
    Returns: renders results.html view.
    """

    user_ids = search_module.get_common_search_info(request)

    search_obj = Search(ip=get_ip(request),
                        country=None,
                        education=None,
                        profession=None,
                        experience=None,
                        text=search_module.get_text_from_request(request),
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

    return render(request, cts.RESULTS_VIEW_PATH, params)


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


def send_signup_emails(business_user, language_code, campaign):

    if campaign is None:
        body_filename = 'business_signup_notification_email_body'
        body_input = 'business_signup_email_body'
    else:
        body_filename = 'business_start_signup_notification_email_body'
        body_input = 'business_start_signup_email_body'

    # TODO: make producer consumer work!
    """
    PendingEmail.add_to_queue(candidates=business_user,
                              language_code=language_code,
                              body_input=body_input,
                              subject=_('Welcome to PeakU'),
                              email_type=email_type)
    """

    try:

        BusinessUserPendingEmail.add_to_queue(business_users=business_user,
                                              language_code=language_code,
                                              body_input=body_input,
                                              subject=_('Welcome to PeakU'),
                                              email_type=EmailType.objects.get(name='business welcome'))
        email_sender.send_internal(contact=business_user,
                                   language_code=language_code,
                                   body_filename=body_filename,
                                   subject='Business User acaba de registrarse!!!',
                                   campaign=campaign)
    except (smtplib.SMTPRecipientsRefused, smtplib.SMTPAuthenticationError, UnicodeEncodeError) as e:
        pass


def first_sign_in(signup_form, campaign, request):
    """
    This method is used to do stuff after validating signup-data. Also logs in.
    Args:
        signup_form: Form obj
        request: HTTP obj
        campaign: campaign object
    Returns: None, first auth and sign-in, saves objects
    """

    signup_form.save()
    username = signup_form.cleaned_data.get('username')
    password = signup_form.cleaned_data.get('password1')

    # Creates a Authentication user
    auth_user = authenticate(username=username,
                             password=password)

    # New BusinessUser pointing to the AuthUser
    business_user = business.models.BusinessUser(name=request.POST.get('name'),
                                                 email=request.POST.get('username'),
                                                 phone=request.POST.get('phone'),
                                                 ip=get_ip(request),
                                                 plan=get_plan(request),
                                                 auth_user=auth_user)

    business_user.save()

    login(request, auth_user)

    send_signup_emails(business_user, request.LANGUAGE_CODE, campaign)

    return business_user


def popup_signup(request):
    """
    Args:
        request: HTTP obj
    Returns: Redirects.
    """

    signup_form = CustomUserCreationForm(request.POST)

    if signup_form.is_valid():
        campaign = None
        first_sign_in(signup_form, campaign, request)
        return redirect(request.POST.get('result_path'))
    else:

        path = request.POST.get('result_path')
        if path is not None:
            # last part of url is result_id
            result_id = int(path.split('/')[-1])
            return render_result(request, result_id)
        else:
            # Defensive programming: not the best, but better than an error.
            # We have lost the result_id
            return redirect('business:search')


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


def get_first_error_message(form):
    """
    :param form: AuthenticationForm or UserCreationForm
    :return: str with first error_message
    """
    error_messages = [m[0] for m in form.errors.values()]
    if len(error_messages) > 0:  # Takes first element from the errors dictionary
        error_message = error_messages[0]
    else:
        error_message = 'unknown error'
    return error_message


def simple_login_and_business_user(login_form, request):
    """
    :param login_form: a AuthenticationForm object
    :param request: HTTP
    :return: BusinessUser obj
    """
    username = login_form.cleaned_data.get('username')
    password = login_form.cleaned_data.get('password')

    # Creates a Authentication user
    auth_user = authenticate(username=username,
                             password=password)

    login(request, auth_user)

    return BusinessUser.objects.get(auth_user=auth_user)


def home(request):
    """
    Leads to Dashboard view.
    Args:
        request: HTTP request.
    Returns: displays all offers of a business
    """

    login_form = AuthenticationForm(data=request.POST)

    # TODO: generalize to set of blocked emails.
    if login_form.is_valid() and request.POST.get('username') != 'g.comercialrmi2@redmilatam.com':  # Block access

        business_user = simple_login_and_business_user(login_form, request)
        return redirect('campañas/{}'.format(business_user.pk))
    else:
        error_message = get_first_error_message(login_form)
        return render(request, cts.BUSINESS_LOGIN, {'error_message': error_message})


def send_contact_emails(contact, language_code):

    try:
        email_sender.send(objects=contact,
                          language_code=language_code,
                          body_input='business_contact_email_body',
                          subject=_('Welcome to PeakU'))
        email_sender.send_internal(contact=contact,
                                   language_code=language_code,
                                   body_filename='contact_notification_email_body',
                                   subject='Business User acaba de llenar formulario de contacto!!!')
    except (smtplib.SMTPRecipientsRefused, smtplib.SMTPAuthenticationError, UnicodeEncodeError) as e:  # cannot send emails
        pass


def contact_form(request):

    return render(request, cts.CONTACT_FORM_VIEW_PATH)


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


def start(request):
    """
    Only displays initial view.
    """

    requirement_bullet_id = BulletType.objects.get(name='requirement').id
    perk_bullet_id = BulletType.objects.get(name='perk').id
    city = common.get_city(request)

    return render(request, cts.START_VIEW_PATH, {'requirement_bullet_id': requirement_bullet_id,
                                                 'perk_bullet_id': perk_bullet_id,
                                                 'error_message': '',
                                                 'work_areas': common.translate_list_of_objects(WorkArea.objects.all(), request.LANGUAGE_CODE),
                                                 'cities': common.get_cities(),
                                                 'default_city': city})


@login_required
def create(request):
    """
    Displays creation of campaign but no registration form.
    """

    requirement_bullet_id = BulletType.objects.get(name='requirement').id
    perk_bullet_id = BulletType.objects.get(name='perk').id

    return render(request, cts.CREATE_VIEW_PATH, {'requirement_bullet_id': requirement_bullet_id,
                                                  'perk_bullet_id': perk_bullet_id,
                                                  'business_user_id': request.POST.get('business_user_id'),
                                                  'work_areas': common.translate_list_of_objects(WorkArea.objects.all(), request.LANGUAGE_CODE)
                                                  })


@login_required
def create_post(request):
    """
    Args:
        request: HTTP post request
    Returns: Renders form.html
    """

    business_user = BusinessUser.objects.get(auth_user=request.user)

    campaign = campaign_module.create_campaign(request)
    business_user.campaigns.add(campaign)
    business_user.save()

    return redirect('tablero_de_control/{business_pk}?campaign_id={campaign_pk}'.format(business_pk=business_user.pk,
                                                                                        campaign_pk=campaign.pk))


def start_post(request):
    """
    Args:
        request: HTTP post request
    Returns: Renders form.html.
    """

    signup_form = CustomUserCreationForm(request.POST)

    if signup_form.is_valid():

        campaign = campaign_module.create_campaign(request)
        business_user = first_sign_in(signup_form, campaign, request)
        business_user.campaigns.add(campaign)
        business_user.save()

        #return redirect('resumen/{business_pk}?campaign_id={campaign_pk}'.format(business_pk=business_user.pk,
        #                                                                         campaign_pk=campaign.pk))
        return redirect('tablero_de_control/{business_pk}?campaign_id={campaign_pk}'.format(business_pk=business_user.pk,
                                                                                            campaign_pk=campaign.pk))

    else:

        error_message = get_first_error_message(signup_form)
        return render(request, cts.START_VIEW_PATH, {'error_message': error_message,
                                                     'work_areas': common.translate_list_of_objects(
                                                         WorkArea.objects.all(), request.LANGUAGE_CODE),
                                                     'cities': common.get_cities()})


def business_signup(request):

    signup_form = CustomUserCreationForm(request.POST)

    if signup_form.is_valid():

        campaign = None
        # TODO: save the company field
        first_sign_in(signup_form, campaign, request)

        return render(request, cts.BUSINESS_CAMPAIGNS_VIEW_PATH)
    else:

        error_message = get_first_error_message(signup_form)
        return render(request, cts.INDEX_VIEW_PATH, {'error_message': error_message})


@login_required
def business_campaigns(request, business_user_id):

    business_user = BusinessUser.objects.get(pk=business_user_id)

    if request.user.id != business_user.auth_user.id:
        return redirect('business:login')

    campaigns = business_user.campaigns.all()

    return render(request, cts.BUSINESS_CAMPAIGNS_VIEW_PATH, {'campaigns': campaigns,
                                                              'business_user_id': business_user.pk
                                                              })


@login_required
def dashboard(request, business_user_id, campaign_id, state_name):
    """
    Renders the business dashboard
    Args:
        request: HTTP
        business_user_id: BusinessUser primary key
        campaign_id: Campaign pk
        state_name: name str
    """

    business_user = BusinessUser.objects.get(pk=business_user_id)
    campaign = Campaign.objects.get(pk=campaign_id)

    if request.user.id != business_user.auth_user.id or campaign not in business_user.campaigns.all():
        return redirect('business:login')

    # TODO: remove?
    dashboard_module.send_email_from_dashboard(request, campaign)

    all_params = dashboard_module.get_dashboard_params(campaign)

    return render(request, cts.DASHBOARD_VIEW_PATH, {'candidates': all_params[state_name],
                                                     'campaign': campaign,
                                                     'state_name': state_name})


def candidate_profile(request, pk):
    candidate = Candidate.objects.get(pk=pk)
    return render(request, cts.CANDIDATE_PROFILE_VIEW_PATH, {'candidate': candidate})


def signup_choice(request):
    return render(request, cts.SIGNUP_CHOICE_VIEW_PATH, {})


def business_applied(request):
    return render(request, cts.BUSINESS_APPLIED_VIEW_PATH, {})


@login_required
def summary(request, campaign_id):
    business_user = get_business_user(request)
    campaign = Campaign.objects.get(pk=campaign_id)

    if request.user.id != business_user.auth_user.id or campaign not in business_user.campaigns.all():
        return redirect('business:login')

    all_params = dashboard_module.get_dashboard_params(campaign)

    num_applicants = len(all_params['applicants'])
    num_relevant = len(all_params['relevant'])
    num_recommended = len(all_params['recommended'])
    num_rejected = len(all_params['rejected'])

    return render(request, cts.SUMMARY_VIEW_PATH, {'business_user': business_user,
                                                   'campaign': campaign,
                                                   'num_applicants': num_applicants,
                                                   'num_relevant': num_relevant,
                                                   'num_recommended': num_recommended,
                                                   'num_rejected': num_rejected,
                                                   'total_candidates': num_applicants + num_recommended + num_rejected + num_relevant})
