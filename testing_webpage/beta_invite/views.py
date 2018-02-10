import os
from user_agents import parse
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render

import common
from ipware.ip import get_ip
from beta_invite import constants as cts
from beta_invite.util import email_sender
from beta_invite import interview_module
from beta_invite.models import User, Visitor, Profession, Education, Country, Campaign, Trade, TradeUser, Bullet, BulletType, Test, Question, Score, Evaluation
from beta_invite import test_module, new_user_module


def index(request):
    """
    This view works for both user and business versions. It is displayed on 3 different urls: peaku.co, /business,
    /beta_invite
    :param request: can come with args "name" and "email", if not it will load the initial page.
    :return: renders a view.
    """

    return render(request, cts.INTRO_VIEW_PATH)


# TODO: Localization a las patadas
def translate_list_of_objects(objects, language_code):
    """Assigns to field name the language specific one."""
    if 'es' in language_code:
        for o in objects:
            o.name = o.name_es


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

    education = Education.objects.all().order_by('level')
    translate_list_of_objects(education, language_code)

    countries = Country.objects.all().order_by('name')

    return countries, education, professions


def get_trade_drop_down_values(language_code):
    """
    Gets lists of drop down for trades.
    Args:
        language_code: 2 digit code (eg. 'es')
    Returns: A tuple containing (Countries, Education, Professions)
    """

    trades = Trade.objects.all().order_by(get_name_field(language_code))
    translate_list_of_objects(trades, language_code)

    countries = Country.objects.all().order_by('name')

    return countries, trades


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


def long_form(request):
    """
    will render a form to input user data.
    """

    # Gets information of client: such as if it is mobile
    ua_string = request.META['HTTP_USER_AGENT']
    is_desktop = not parse(ua_string).is_mobile

    # Passes campaign_id around to collect it in the POST form from this view: cts.LONG_FORM_VIEW_PATH.
    # Also uses campaign to customize view.
    # If campaign_id is not found; will default to the default_campaign.
    campaign_id = request.GET.get('campaign_id', cts.DEFAULT_CAMPAIGN_ID)
    campaign = Campaign.objects.filter(pk=campaign_id).first()
    campaign.translate(request.LANGUAGE_CODE)

    ip = get_ip(request)
    action_url = '/servicio_de_empleo/post'
    countries, education, professions = get_drop_down_values(request.LANGUAGE_CODE)

    Visitor(ip=ip, ui_version=cts.UI_VERSION, is_mobile=not is_desktop).save()

    perks = campaign.bullets.filter(bullet_type__in=BulletType.objects.filter(name='perk'))
    requirements = campaign.bullets.filter(bullet_type__in=BulletType.objects.filter(name='requirement'))

    param_dict = {'main_message': _("Discover your true passion"),
                  'action_url': action_url,
                  'countries': countries,
                  'education': education,
                  'professions': professions,
                  'job_title': campaign.title,
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

    return render(request, cts.LONG_FORM_VIEW_PATH, param_dict)


def update_search_dictionary_on_background():
    """
    A background process is spawned to update internal search structures.
    First it goes into the subscribe directory, then it updates the missing text extractions. Then it generates the
    user_relevance_dictionary.p
    Returns: None
    """
    command = 'cd subscribe/ && python3 document_reader.py && python3 search_engine.py &'
    os.system(command)


def post_long_form(request):
    """
    Args:
        request: Request object
    Returns: Saves or updates the User, now it will not be creating new user objects for the same email.
    """
    # Gets information of client: such as if it is mobile.
    ua_string = request.META['HTTP_USER_AGENT']
    is_mobile = parse(ua_string).is_mobile
    ip = get_ip(request)

    profession_id = request.POST.get('profession')
    education_id = request.POST.get('education')
    country_id = request.POST.get('country')

    campaign = common.get_campaign_from_request(request)

    tests = translate_tests(campaign.tests.all(), request.LANGUAGE_CODE)

    end_point_params = {'main_message': _("Discover your true passion"),
                        'secondary_message': _("We search millions of jobs and find the right one for you"),
                        'campaign_id': campaign.id,
                        'tests': tests,
                        'question_ids': test_module.get_tests_questions_dict(tests),
                        }

    if profession_id is not None and education_id is not None and country_id is not None:

        profession = Profession.objects.get(pk=profession_id)
        education = Education.objects.get(pk=education_id)
        country = Country.objects.get(pk=country_id)

        user_params = {'name': request.POST.get('name'),
                       'email': request.POST.get('email'),
                       'phone': request.POST.get('phone'),
                       'profession': profession,
                       'education': education,
                       'country': country,
                       'ip': ip,
                       'ui_version': cts.UI_VERSION,
                       'is_mobile': is_mobile,
                       'language_code': request.LANGUAGE_CODE}

        # TODO: update user instead of always creating a new one.
        user = new_user_module.user_if_exists(request.POST.get('email'))

        if user:
            user = new_user_module.update_user(campaign, user, user_params, request)
        else:
            user = new_user_module.create_user(campaign, user_params, request, is_mobile)

        end_point_params['user_id'] = user.id

    else:
        # Adds the user id to the params, to be able to track answers, later on.
        user_id = request.GET.get('user_id')
        if user_id is not None:
            end_point_params['user_id'] = int(user_id)

    return render(request, cts.SUCCESS_VIEW_PATH, end_point_params)


@login_required
def home(request):
    return render(request, 'success.html')


def fast_job(request):
    """
    will render
    """

    # passes campaign_id around to collect it in the POST form from this view: cts.LONG_FORM_VIEW_PATH
    campaign_id = request.GET.get('campaign_id')
    ua_string = request.META['HTTP_USER_AGENT']
    is_mobile = parse(ua_string).is_mobile

    ip = get_ip(request)
    action_url = '/fast_job/post'
    countries, trades = get_trade_drop_down_values(request.LANGUAGE_CODE)

    Visitor(ip=ip, ui_version=cts.UI_VERSION, is_mobile=is_mobile).save()

    param_dict = {'main_message': _("Find a job now"),
                  'secondary_message': _("We search millions of jobs and find the right one for you"),
                  'action_url': action_url,
                  'countries': countries,
                  'trades': trades,
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

    return render(request, cts.FAST_JOB_VIEW_PATH, param_dict)


def post_fast_job(request):
    """
    Args:
        request: Request object
    Returns: Saves
    """
    # Gets information of client: such as if it is mobile.
    ua_string = request.META['HTTP_USER_AGENT']
    user_agent = parse(ua_string)
    ip = get_ip(request)

    trade_id = request.POST.get('trade')
    country_id = request.POST.get('country')

    trade = Trade.objects.get(pk=trade_id)
    country = Country.objects.get(pk=country_id)

    # finally collects the campaign_id.
    campaign_id = request.POST.get('campaign_id')

    trade_user = TradeUser(name=request.POST.get('name'),
                           email=request.POST.get('email'),
                           phone=request.POST.get('phone'),
                           country=country,
                           trade=trade,
                           description=request.POST.get('description'),
                           ip=ip,
                           ui_version=cts.UI_VERSION,
                           is_mobile=user_agent.is_mobile)

    # verify that the campaign exists.
    if campaign_id:
        try:
            campaign = Campaign.objects.get(pk=int(campaign_id))
            # under right conditions add the campaign before saving
            trade_user.campaign = campaign
        except ObjectDoesNotExist:
            pass

    # Saves here to get an id
    trade_user.save()

    # TODO: add welcoming email

    return render(request, cts.SUCCESS_VIEW_PATH, {'main_message': _("Find a job now"),
                                                   'secondary_message': _("We search millions of jobs and find the right one for you"),
                                                   })


def send_interview_mail(email_template, candidate):
    """
    Args:
        email_template: name of email body, in beta_invite/util.
        candidate: Object.
    Returns: sends email.
    """
    if candidate and interview_module.has_recorded_interview(candidate.campaign):
        candidate.campaign.translate(candidate.user.language_code)

        email_sender.send_to_candidate(candidates=candidate,
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

    # test_score_str = ''  # by default there is no score unless the test was done.

    test_done = test_module.comes_from_test(request)

    if test_done:

        cut_scores, scores = test_module.get_scores(campaign, user_id, questions_dict, request)

        has_scores = (len(scores) > 0)

        if has_scores:
            test_module.get_evaluation(cut_scores, scores, campaign, user_id)

    return render(request, cts.INTERVIEW_VIEW_PATH, {'candidate': candidate})


    '''
    test_score_str = '({}/100)'.format(round(evaluation.final_score))

    has_recorded_interview = interview_module.has_recorded_interview(campaign)
    has_calendly = campaign.calendly
    if not test_done or evaluation.passed:

        # send_interview_mail('user_interview_email_body', candidate)

        right_button_action = interview_module.adds_campaign_and_user_to_url('interview/1', user_id, campaign.id)

        return render(request, cts.INTERVIEW_VIEW_PATH, {'campaign': campaign,
                                                         'question_video': common.get_intro_video(),
                                                         'ziggeo_api_key': common.get_ziggeo_api_key(),
                                                         'top_message': interview_module.get_top_message(on_interview=False,
                                                                                                         has_calendly=has_calendly,
                                                                                                         has_recorded_interview=has_recorded_interview).format(test_score_str=test_score_str),
                                                         'message0': interview_module.get_message0(on_interview=False),
                                                         'message1': '',
                                                         'message2': interview_module.get_message2(has_recorded_interview, has_calendly),
                                                         'left_button_text': _('Schedule Interview'),
                                                         'right_button_text': _('Record interview now!'),
                                                         'left_button_action': campaign.calendly_url,
                                                         'right_button_action': right_button_action,
                                                         'enable_recording': False,
                                                         'has_recorded_interview': has_recorded_interview,
                                                         'has_calendly': has_calendly,
                                                         'left_button_is_back': False,
                                                         'on_interview': False,
                                                         })
                                                         
    else:  # doesn't pass test.
        return render(request, cts.SUCCESS_VIEW_PATH, {'main_message': _("Discover your true passion"),
                                                       'secondary_message': _("We search millions of jobs and find the right one for you"),
                                                       })  
                                                       '''


def interview(request, pk):
    """
    Endpoint to get the next question.
    Args:
        request: HTTP
        pk: primary key. In this case the question order.
    Returns:
    """
    # change names to improve readability
    question_number = int(pk)

    campaign = common.get_campaign_from_request(request)
    has_calendly = campaign.calendly

    # TODO: assumes campaign has only one interview.
    interview_obj = campaign.interviews.all()[0]

    user = common.get_user_from_request(request)
    user_id = user.id if user else None
    token = request.POST.get('new_video_token')
    interview_module.save_response(campaign, user, question_number, interview_obj, token)

    left_button_action = interview_module.get_previous_url(question_number, campaign.id, user_id)
    interview_module.update_candidate_state(campaign, user, interview_obj, question_number)

    try:
        next_question = interview_obj.questions.get(order=question_number)
        answer_video = interview_module.fetch_current_video_answer(campaign, user, next_question)
        next_question.translate(request.LANGUAGE_CODE)
        has_recorded_interview = True
        right_button_text = interview_module.get_right_button_text(interview_obj, next_question)
        right_button_action = interview_module.get_right_button_action(question_number, user_id, campaign.id)
        enable_recording = True
        question_video = next_question.video_token
        message1 = next_question.text
        message2 = ''

    except ObjectDoesNotExist:  # beyond last question
        right_button_text = ''
        right_button_action = ''
        has_recorded_interview = False
        enable_recording = False
        question_video = ''
        message1 = ''
        message2 = _('Thanks for completing the interview, we will contact you soon ;)')
        answer_video = None

    return render(request, cts.INTERVIEW_VIEW_PATH, {'campaign': campaign,
                                                     'ziggeo_api_key': common.get_ziggeo_api_key(),
                                                     'question_video': question_video,
                                                     'top_message': interview_module.get_top_message(on_interview=True,
                                                                                                     has_calendly=has_calendly,
                                                                                                     has_recorded_interview=has_recorded_interview),
                                                     'message0': interview_module.get_message0(on_interview=has_recorded_interview),
                                                     'message1': message1,
                                                     'message2': message2,
                                                     'left_button_text': _('Back'),
                                                     'right_button_text': right_button_text,
                                                     'right_button_action': right_button_action,
                                                     'left_button_action': left_button_action,
                                                     'enable_recording': enable_recording,
                                                     'has_recorded_interview': has_recorded_interview,
                                                     'has_calendly': has_calendly,
                                                     'left_button_is_back': True,
                                                     'on_interview': True,
                                                     'answer_video': answer_video,
                                                     })


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
        user.curriculum_url = new_user_module.save_curriculum_from_request(request, user, 'curriculum')
        user.save()
        return render(request, cts.SUCCESS_VIEW_PATH, {})

    # if any inconsistency, then do nothing, ignore it.
    return render(request, cts.ADD_CV, {})
