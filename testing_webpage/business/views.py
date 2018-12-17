import os
import json
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.testing_webpage.settings')
application = get_wsgi_application()

import smtplib
import hashlib
from datetime import datetime
from django.contrib.auth.decorators import login_required
from ipware.ip import get_ip
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import login, authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.forms import AuthenticationForm
from django.utils import formats
from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse
from decouple import config
from django.db import models
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

import common
import business
import beta_invite

from beta_invite.util import messenger_sender
from business import search_module, prospect_module
from beta_invite.util import email_sender
from business import constants as cts
from beta_invite.models import User, WorkArea, EmailType, Campaign, Test, Price, CampaignState
from business.models import Plan, Contact, Search, BusinessUser, Company
from beta_invite.models import Requirement
from business.custom_user_creation_form import CustomUserCreationForm
from dashboard import campaign_module
from dashboard.models import Candidate, BusinessState, Comment
from business import dashboard_module
from testing_webpage.models import BusinessUserPendingEmail, CampaignPendingEmail


TAX = 0.19
DEFAULT_BASE_PRICE = 0
INVALID_WORK_AREAS = [8, 14, 17]


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
        BusinessUserPendingEmail.add_to_queue(business_users=business_user,
                                              language_code=language_code,
                                              body_input=body_input,
                                              subject=_('Welcome to PeakU'),
                                              email_type=EmailType.objects.get(name='business_welcome'))
    else:
        body_filename = 'business_start_signup_notification_email_body'
        body_input = 'business_start_signup_email_body'
        messenger_sender.send(objects=campaign,
                              language_code=language_code,
                              body_input=body_input)
        CampaignPendingEmail.add_to_queue(campaigns=campaign,
                                          language_code=language_code,
                                          body_input=body_input,
                                          subject='Oferta publicada exitosamente - {campaign_name}',
                                          email_type=EmailType.objects.get(name='business_welcome'))

    email_sender.send_internal(contact=business_user,
                               language_code=language_code,
                               body_filename=body_filename,
                               subject='Business User acaba de registrarse!!!',
                               campaign=campaign)


def first_sign_in(signup_form, request):
    """
    This method is used to do stuff after validating signup-data. Also logs in.
    Args:
        signup_form: Form obj
        request: HTTP obj
    Returns: None, first auth and sign-in, saves objects
    """

    signup_form.save()
    username = signup_form.cleaned_data.get('username')
    password = signup_form.cleaned_data.get('password1')

    # Creates a Authentication user
    auth_user = authenticate(username=username,
                             password=password)

    company = Company(name=request.POST.get('company'))
    company.save()

    # New BusinessUser pointing to the AuthUser
    business_user = business.models.BusinessUser(name=request.POST.get('name'),
                                                 company=company,
                                                 email=request.POST.get('username'),
                                                 phone=request.POST.get('phone'),
                                                 ip=get_ip(request),
                                                 plan=get_plan(request),
                                                 auth_user=auth_user)

    business_user.save()

    login(request, auth_user)

    return business_user


def get_business_user(request):
    """
    Given a request that has the AuthUser.id will get the BusinessUser
    Args:
        request: HTTP request object.
    Returns: A BusinessUser object.
    """
    return BusinessUser.objects.get(auth_user_id=request.user.id)


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
    if login_form.is_valid():

        business_user = simple_login_and_business_user(login_form, request)
        if request.POST.get('username') == 'admin@peaku.co':
            return redirect(common.get_host()+'/dashboard')
        else:
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
    except (smtplib.SMTPRecipientsRefused, smtplib.SMTPAuthenticationError, UnicodeEncodeError) as e:
        pass


def contact_form(request):
    return render(request, cts.CONTACT_FORM_VIEW_PATH)


def contact_form_post(request):
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


def start(request):
    """
    Only displays initial view.
    """

    city = common.get_city(request)

    return render(request, cts.START_VIEW_PATH, {'error_message': '',
                                                 'work_areas': common.translate_list_of_objects(WorkArea.objects.all(), request.LANGUAGE_CODE),
                                                 'cities': common.get_cities(),
                                                 'default_city': city,
                                                 'requirements': Requirement.objects.all(),
                                                 'tests': Test.objects.filter(public=True).order_by('name_es')})


def send_new_campaign_notification(business_user, language_code, campaign):

    body_filename = 'business_new_campaign_notification_email_body'

    try:

        email_sender.send_internal(contact=business_user,
                                   language_code=language_code,
                                   body_filename=body_filename,
                                   subject='Un usuario ya registrado ha creado una nueva campaña',
                                   campaign=campaign)
    except (smtplib.SMTPRecipientsRefused, smtplib.SMTPAuthenticationError, UnicodeEncodeError):
        pass


# This for create campaign when the user is logged
@login_required
def create_post(request):
    """
    Args:
        request: HTTP post request
    Returns: Renders form.html
    """

    business_user = BusinessUser.objects.get(auth_user=request.user)
    campaign, prospects = campaign_module.create_campaign(request)
    business_user.campaigns.add(campaign)
    business_user.save()
    if not business_user.is_peaku():
        prospect_module.send_mails(prospects)
        messenger_sender.send(objects=prospects,
                              language_code='es',
                              body_input='candidate_prospect')

    send_new_campaign_notification(business_user, request.LANGUAGE_CODE, campaign)
    #PublicPost.add_to_public_post_queue(campaign)

    return redirect('resumen/{campaign_pk}'.format(campaign_pk=campaign.pk))


def start_post(request):
    """
    Args:
        request: HTTP post request
    Returns: Renders form.html.
    """

    signup_form = CustomUserCreationForm(request.POST)

    if signup_form.is_valid():

        campaign, prospects = campaign_module.create_campaign(request)
        business_user = first_sign_in(signup_form, request)
        business_user.campaigns.add(campaign)
        business_user.save()
        send_signup_emails(business_user, request.LANGUAGE_CODE, campaign)

        #PublicPost.add_to_public_post_queue(campaign)
        if not business_user.is_peaku():
            prospect_module.send_mails(prospects)
            messenger_sender.send(objects=prospects,
                                  language_code='es',
                                  body_input='candidate_prospect')

        return redirect('tablero-de-control/{business_user_id}/{campaign_id}/applicants'.format(business_user_id=business_user.pk,
                                                                                                campaign_id=campaign.pk))

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
        business_user = first_sign_in(signup_form, request)
        send_signup_emails(business_user, request.LANGUAGE_CODE, campaign)

        return render(request, cts.BUSINESS_CAMPAIGNS_VIEW_PATH)
    else:

        error_message = get_first_error_message(signup_form)
        return render(request, cts.INDEX_VIEW_PATH, {'error_message': error_message})


@login_required
def business_campaigns(request, business_user_id):

    business_user = BusinessUser.objects.get(pk=business_user_id)

    if request.user.id != business_user.auth_user.id:
        return redirect('business:login')

    campaigns = business_user.campaigns.filter(removed=False).order_by('-created_at', 'state', 'title_es').all()
    currency = 'COP'
    date = str(datetime.now())
    invalid_work_areas = INVALID_WORK_AREAS

    if settings.DEBUG:
        action_url = "https://sandbox.checkout.payulatam.com/ppp-web-gateway-payu/"
        apikey = '4Vj8eK4rloUd272L48hsrarnUA'
        merchant_id = '508029'
        account_id = '512321'
        test = '1'
        host = 'http://127.0.0.1:8000/'
    else:
        action_url = "https://checkout.payulatam.com/ppp-web-gateway-payu"
        apikey = config('payu_api_key')
        merchant_id = config('merchant_id')
        account_id = config('account_id')
        test = '0'
        host = 'https://peaku.co/'

    response_url = host + 'seleccion_de_personal/resumen/'
    confirmation_url = host + 'seleccion_de_personal/payment_confirmation'
    for c in campaigns:
        if c.salary_high_range:
            c.reference_code = str(c.id) + "-" + date
            try:
                c.base = round(float(Price.objects.get(work_area=c.work_area,
                                                       from_salary__lt=c.salary_high_range,
                                                       to_salary__gte=c.salary_high_range).price))
            except models.ObjectDoesNotExist:
                c.base = DEFAULT_BASE_PRICE
            if c.id == 395:
                c.base = 9000
            c.tax = round(c.base * TAX, 2)
            c.amount = round(float(c.base+c.tax), 2)
            c.amount = str(c.amount)
            c.tax = str(c.tax)
            c.base = str(c.base)
            c.signature = hashlib.md5((apikey + "~" + merchant_id + "~" + c.reference_code + "~" + str(c.amount) + "~" + currency).encode('utf-8')).hexdigest()

    return render(request, cts.BUSINESS_CAMPAIGNS_VIEW_PATH, {'campaigns': campaigns,
                                                              'business_user_id': business_user.pk,
                                                              'action_url': action_url,
                                                              'apikey': apikey,
                                                              'merchant_id': merchant_id,
                                                              'account_id': account_id,
                                                              'currency': currency,
                                                              'test': test,
                                                              'description': 'Activación de la oferta Premium',
                                                              'buyer_name': business_user.name,
                                                              'buyer_email': business_user.email,
                                                              'invalid_work_areas': invalid_work_areas,
                                                              'response_url': response_url,
                                                              'confirmation_url': confirmation_url,
                                                              'state_name': 'relevant',
                                                              })


@csrf_exempt
def payment_confirmation(request):

    # This is Payu transaction approved code, only for confirmation page, not global variable
    PAYU_APPROVED_CODE = '4'

    if settings.DEBUG:
        campaign_id = '1'
        transaction_final_state = PAYU_APPROVED_CODE
        sign = '1234'
        create_signature = '1234'
    else:
        transaction_final_state = request.POST.get('state_pol')
        response_code_pol = request.POST.get('response_code_pol')
        payment_method_type = request.POST.get('payment_method_type')
        currency = request.POST.get('currency')
        payment_method_id = request.POST.get('payment_method_id')
        response_message_pol = request.POST.get('response_message_pol')
        campaign_id = request.POST.get('extra1')
        apikey = config('payu_api_key')
        sign = request.POST.get('sign')
        merchant_id = request.POST.get('merchant_id')
        reference_sale = request.POST.get('reference_sale')
        amount = request.POST.get('value')

        # Decimal validation, Payu requirement
        if amount[-1] == 0:
            amount = round(float(amount), 1)

        # Important validation to check the integrity of the data
        create_signature = hashlib.md5((apikey + "~" + merchant_id + "~" + reference_sale + "~" + str(amount) + "." + "~" + currency + "~" + transaction_final_state).encode('utf-8')).hexdigest()

    campaign_id = int(campaign_id)
    campaign = Campaign.objects.get(pk=campaign_id)

    if transaction_final_state == PAYU_APPROVED_CODE:
        campaign.state = CampaignState.objects.get(code='A')
        campaign.free_trial = False
        campaign.save()
        if create_signature == sign:
            message = '<h1>0K</h1>'
        else:
            message = '<h1>Sign is wrong check why!!!</h1>'
        return HttpResponse(message, status=200)
    else:
        message = '<h1>Something is wrong</h1>' + transaction_final_state
        return HttpResponse(message, status=400)


def candidate_profile(request, pk):

    candidate = Candidate.objects.get(pk=pk)
    business_user = get_business_user(request)
    phone = candidate.user.phone.replace('+', '')

    return render(request, cts.CANDIDATE_PROFILE_VIEW_PATH, {'candidate': candidate,
                                                             'business_user': business_user,
                                                             'phone': phone})


@login_required
def summary(request, campaign_id, business_user=None):

    campaign = Campaign.objects.get(pk=campaign_id)
    common.calculate_evaluation_summaries_with_caching(campaign)

    if business_user is None:
        business_user = get_business_user(request)
        if common.access_for_users(request, campaign, business_user):
            return redirect('business:login')

    created_at = formats.date_format(campaign.created_at, "DATE_FORMAT")

    return render(request, cts.SUMMARY_VIEW_PATH, {'business_user': business_user,
                                                   'campaign': campaign,
                                                   'num_total': common.get_application_candidates_count(campaign) + common.get_relevant_candidates_count(campaign),
                                                   'num_applicants': common.get_application_candidates_count(campaign),
                                                   'num_relevant': common.get_relevant_candidates_count(campaign),
                                                   'num_recommended': common.get_recommended_candidates_count(campaign),
                                                   'created_at': created_at})


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
    logged_user = BusinessUser.objects.get(auth_user_id=request.user.id)
    campaign = Campaign.objects.get(pk=campaign_id)
    business_state = BusinessState.objects.get(name=state_name)
    business_state.translate(request.LANGUAGE_CODE)

    if common.access_for_users(request, campaign, business_user):
        return redirect('business:login')

    dashboard_module.send_email_from_dashboard(request, campaign)
    common.calculate_evaluation_summaries_with_caching(campaign)

    applicants = []
    relevant = []
    recommended = []

    if business_state.name == 'aplicantes':
        applicants = common.get_application_candidates(campaign)
        campaign_evaluation = campaign.applicant_evaluation_last
        campaign_state_name = 'prospectos'

    elif business_state.name == 'relevantes':
        relevant = common.get_relevant_candidates(campaign)
        campaign_evaluation = campaign.relevant_evaluation_last
        campaign_state_name = 'pre-seleccionados'

    else:
        recommended = common.get_recommended_candidates(campaign)
        campaign_evaluation = campaign.recommended_evaluation_last
        campaign_state_name = 'seleccionados'

    return render(request, cts.DASHBOARD_VIEW_PATH, {'candidates': {'applicants': applicants,
                                                                    'relevant': relevant,
                                                                    'recommended': recommended}[state_name],
                                                     'campaign': campaign,
                                                     'business_state': business_state,
                                                     'applicants': applicants,
                                                     'relevant': relevant,
                                                     'recommended': recommended,
                                                     'business_user': business_user,
                                                     'total_applicants': len(applicants),
                                                     'total_recommended': len(recommended),
                                                     'total_relevant': len(relevant),
                                                     'campaign_evaluation': campaign_evaluation,
                                                     'campaign_state_name': campaign_state_name,
                                                     'logged_user': logged_user.name
                                                     })


def save_comments(request):

    if request.method == 'POST':
        candidate = common.get_candidate_from_request(request)
        comment = Comment(text=request.POST.get('comment'))
        comment.save()
        candidate.comments.add(comment)
        candidate.save()
        return HttpResponse(comment.text)
    else:
        return HttpResponseBadRequest('<h1>HTTP CODE 400: Client sent bad request with missing params</h1>')


def online_demo(request):

    campaign_id = 156
    campaign = Campaign.objects.get(pk=campaign_id)
    business_user = common.get_business_user_with_campaign(campaign)

    # removes login decorator
    s = summary.__wrapped__
    return s(request, campaign_id, business_user=business_user)


def get_work_area_requirement(request, work_area_id):

    requirements = Requirement.objects.filter(work_area_id=work_area_id)

    json_data = json.dumps([{'pk': k.pk, 'name': k.name} for k in requirements])

    return JsonResponse(json_data, safe=False)


def send_demo_scheduled_notification(request, contact):

    try:
        email_sender.send(objects=contact,
                          language_code=request.LANGUAGE_CODE,
                          body_input='business_contact_email_body',
                          subject=_('Welcome to PeakU'))
        email_sender.send_internal(contact=contact,
                                   language_code=request.LANGUAGE_CODE,
                                   body_filename='demo_sheduled_notification_email_body',
                                   subject='Se ha programado un demo!!!!!')

    except (smtplib.SMTPRecipientsRefused, smtplib.SMTPAuthenticationError, UnicodeEncodeError) as e:
        pass


def demo_scheduled(request):

    contact = Contact(name=request.POST.get('name'),
                      email=request.POST.get('email'),
                      phone=request.POST.get('phone'),)

    contact.save()

    send_demo_scheduled_notification(request, contact)

    return render(request, cts.DEMO_SCHEDULED_VIEW_PATH)


def change_state(request):

    if request.method == 'POST':
        candidate = Candidate.objects.get(pk=request.POST.get('candidate_id'))
        campaign = candidate.campaign
        state_code = request.POST.get('state_code')

        if state_code:
            if state_code == 'ABC':
                campaign.likes = campaign.likes + 1
                campaign.save()
                candidate.change_state(state_code=state_code, auth_user=request.user, place='Business User ha seleccionado a este candidato')
                candidate.change_by_client = True
                candidate.liked = True
                candidate.save()
            elif state_code == 'RBC':
                candidate.reason_for_rejection = request.POST.get('reason')
                candidate.change_state(state_code=state_code, auth_user=request.user, place='Business User ha rechazado a este candidato')
                candidate.change_by_client = True
                candidate.save()
            else:
                candidate.change_state(state_code=state_code, auth_user=request.user, place='Admin ha cambiado el estado del candidato')

        print('Tests')

        return HttpResponse()
    else:
        return HttpResponseBadRequest('<h1>HTTP CODE 400: Client sent bad request with missing params</h1>')