import json
from user_agents import parse
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.http import HttpResponseBadRequest, HttpResponse

import common
from ipware.ip import get_ip
from beta_invite import constants as cts
from beta_invite.util import email_sender
from beta_invite import interview_module
from beta_invite.models import User, Visitor, Profession, Education, Country, Campaign, BulletType, Gender, City, Area
from beta_invite import test_module, new_user_module
from django.shortcuts import redirect
from beta_invite.util import messenger_sender, common_senders
from beta_invite.util.email_sender import remove_accents
from dashboard.models import Candidate


# TODO: Localization a las patadas
def translate_list_of_objects(objects, language_code):
    """Assigns to field name the language specific one."""
    if 'es' in language_code:
        for o in objects:
            o.name = o.name_es
    return objects


def get_name_field(language_code):
    if language_code not in 'en':
        return 'name_' + language_code
    else:
        return 'name'


def get_drop_down_values(language_code):
    """
    Gets lists of drop down values for several different fields.
    Args:
        language_code: 2 digit code (eg. 'es')
    Returns: A tuple containing (Countries, Education, Professions)
    """

    professions = Profession.objects.all().order_by(get_name_field(language_code))
    translate_list_of_objects(professions, language_code)
    cities = City.objects.all().order_by('name')
    education = Education.objects.all().order_by('level')
    translate_list_of_objects(education, language_code)

    countries = Country.objects.all().order_by('name')

    return countries, cities, education, professions


def translate_bullets(bullets, lang_code):
    """
    Args:
        bullets: array with bullet Objects
        lang_code: 'es' for example
    Returns: translated array
    """
    a = []
    if lang_code == 'es':

        for b in bullets:
            b.name = b.name_es
            a.append(b)
    else:
        return bullets

    return a


def translate_tests(tests, lang_code):
    """
    Args:
        tests: array with test Objects
        lang_code: 'es' for example
    Returns: translated array
    """
    a = []
    if lang_code == 'es':

        for t in tests:
            t.name = t.name_es
            a.append(t)

        return a
    else:
        return tests


def index(request):
    """
    will render a form to input user data.
    """

    # Gets information of client: such as if it is mobile
    is_desktop = not parse(request.META['HTTP_USER_AGENT']).is_mobile

    # If campaign_id is not found; will default to the default_campaign.
    campaign_id = request.GET.get('campaign_id', cts.DEFAULT_CAMPAIGN_ID)
    campaign = Campaign.objects.filter(pk=campaign_id).first()
    campaign.translate(request.LANGUAGE_CODE)

    ip = get_ip(request)

    Visitor(ip=ip, is_mobile=not is_desktop).save()

    perks = campaign.bullets.filter(bullet_type__in=BulletType.objects.filter(name='perk'))
    requirements = campaign.bullets.filter(bullet_type__in=BulletType.objects.filter(name='requirement'))

    param_dict = {'job_title': campaign.title,
                  'perks': translate_bullets(perks, request.LANGUAGE_CODE),
                  'requirements': translate_bullets(requirements, request.LANGUAGE_CODE),
                  'is_desktop': is_desktop,
                  }

    if campaign_id is not None:
        param_dict['campaign_id'] = int(campaign_id)
        try:
            campaign = Campaign.objects.get(pk=int(campaign_id))
            campaign.translate(request.LANGUAGE_CODE)
            # if campaign exists send it.
            param_dict['campaign'] = campaign
        except ObjectDoesNotExist:
            pass

    return render(request, cts.INDEX_VIEW_PATH, param_dict)


def register(request):
    """
    Args:
        request: Request object
    Returns: Saves or updates the User, now it will not be creating new user objects for the same email.
    """
    # Gets information of client: such as if it is mobile.
    is_mobile = parse(request.META['HTTP_USER_AGENT']).is_mobile

    email = request.POST.get('email')
    name = request.POST.get('name')
    phone = request.POST.get('phone')
    politics_accepted = request.POST.get('politics')
    if politics_accepted:
        politics = True
    else:
        politics = False
    campaign = common.get_campaign_from_request(request)

    # Validates all fields
    if campaign and name and phone and (email or not campaign.has_email):

        country = common.get_country_with_request(request)
        city = common.get_city(request, country)

        user_params = {'name': name,
                       'email': email,
                       'phone': phone,
                       'country': country,
                       'city': city,
                       'ip': get_ip(request),
                       'is_mobile': is_mobile,
                       'language_code': request.LANGUAGE_CODE,
                       'politics': politics}

        # TODO: update user instead of always creating a new one.
        user = new_user_module.user_if_exists(email, phone, campaign)
        if user:
            user = new_user_module.update_user(campaign, user, user_params, request)
        else:
            user = new_user_module.create_user(campaign, user_params, request, is_mobile)

        # TODO: Remove 'if' when ready.
        # Test to showcase new whatsapp feature
        from django.conf import settings  # TODO: remove import also
        if settings.DEBUG:
            messenger_sender.send(candidates=common.get_candidate(user, campaign),
                                  language_code=request.LANGUAGE_CODE,
                                  body_input='candidate_backlog')

        return redirect('/servicio_de_empleo/pruebas?campaign_id={campaign_id}&user_id={user_id}'.format(campaign_id=campaign.id,
                                                                                                         user_id=user.id))

    else:
        return HttpResponseBadRequest('<h1>HTTP CODE 400: Client sent bad request with missing params</h1>')


def tests(request):

    """
    Receives either GET or POST user and campaign ids.
    :param request: HTTP
    :return: renders tests.
    """

    campaign = common.get_campaign_from_request(request)
    tests = translate_tests(campaign.tests.all(), request.LANGUAGE_CODE)

    end_point_params = {'campaign_id': campaign.id,
                        'tests': tests,
                        }

    # Adds the user id to the params, to be able to track answers, later on.
    user = common.get_user_from_request(request)
    candidate = common.get_candidate(user, campaign)
    if user is not None:
        end_point_params['user_id'] = int(user.id)

    if tests:
        return render(request, cts.TESTS_VIEW_PATH, end_point_params)
    else:
        return redirect('/servicio_de_empleo/additional_info?candidate_id={candidate_id}'.format(candidate_id=candidate.pk))


@login_required
def home(request):
    return render(request, 'success.html')


def send_interview_mail(email_template, candidate):
    """
    Args:
        email_template: name of email body, in beta_invite/util.
        candidate: Object.
    Returns: sends email.
    """
    if candidate and interview_module.has_recorded_interview(candidate.campaign):
        candidate.campaign.translate(candidate.user.language_code)

        email_sender.send(objects=candidate,
                          language_code=candidate.user.language_code,
                          body_input=email_template,
                          subject=_('You can record the interview for {campaign}').format(campaign=candidate.campaign.title))


def get_test_result(request):
    """
    Args:
        request: HTTP object
    Returns: Either end process or invites to interview.
    """
    campaign = common.get_campaign_from_request(request)
    questions_dict = test_module.get_tests_questions_dict(campaign.tests.all())
    user = common.get_user_from_request(request)
    user_id = user.id if user else None
    candidate = common.get_candidate(user, campaign)
    name = common_senders.get_first_name(candidate.user.name)

    # test_score_str = ''  # by default there is no score unless the test was done.

    test_done = test_module.comes_from_test(request)

    if test_done:

        cut_scores, scores = test_module.get_scores(campaign, user_id, questions_dict, request)

        has_scores = (len(scores) > 0)

        if has_scores:
            test_module.get_evaluation(cut_scores, scores, campaign, candidate)

    return render(request, cts.TEST_RESULT_VIEW_PATH, {'candidate': candidate, 'campaign': campaign, 'candidate_id': candidate.pk, 'name': name})


def additional_info(request):
    candidate = common.get_candidate_from_request(request)
    param_dict = dict()
    countries, cities, education, professions = get_drop_down_values(request.LANGUAGE_CODE)

    # Dictionary parameters
    param_dict['candidate'] = candidate
    param_dict['genders'] = translate_list_of_objects(Gender.objects.all(), request.LANGUAGE_CODE)
    param_dict['areas'] = translate_list_of_objects(Area.objects.all(), request.LANGUAGE_CODE)
    param_dict['education'] = education
    param_dict['professions'] = professions
    param_dict['countries'] = countries
    param_dict['cities'] = cities

    return render(request, cts.ADDITIONAL_INFO_VIEW_PATH, param_dict)


def save_partial_additional_info(request):

    if request.method == 'POST':
        candidate = common.get_candidate_from_request(request)
        new_user_module.update_user_with_request(request, candidate.user)

        return HttpResponse('')
    else:
        return HttpResponseBadRequest('<h1>HTTP CODE 400: Client sent bad request with missing params</h1>')


def active_campaigns(request):

    candidate = common.get_candidate_from_request(request)
    new_user_module.update_user(candidate.campaign, candidate.user, {}, request)
    return render(request, cts.ACTIVE_CAMPAIGNS_VIEW_PATH)


def add_cv(request):
    """
    When a user registers on a phone, there is no CV field. So the user is left with no CV on his/her profile.
    An email is sent to the user requesting to complete his/her profile by adding the missing CV. This rendering
    displays the missing CV interface.
    Passes around the user_id param. Transitions from GET to POST
    Args:
        request: HTTP
    Returns: Renders simple UI to add a missing CV
    """
    user_id = request.GET.get('user_id')
    return render(request, cts.ADD_CV, {'user_id': user_id})


def add_cv_changes(request):
    """
    Args:
        request: HTTP
    Returns: Adds a CV to the User profile, given that the user exists.
    """

    user_id = request.POST.get('user_id')

    if user_id is not None:
        user = User.objects.get(pk=int(user_id))
        new_user_module.update_resource(request, user, 'curriculum_url', 'resumes')

        return render(request, cts.ACTIVE_CAMPAIGNS_VIEW_PATH, {})

    # if any inconsistency, then do nothing, ignore it.
    return render(request, cts.ADD_CV, {'user_id': user_id})


def security_politics(request):
    return render(request, cts.SECURITY_POLITICS_VIEW_PATH)



