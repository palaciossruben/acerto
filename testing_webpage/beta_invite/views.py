import os
import smtplib
import subprocess
import unicodedata
from user_agents import parse
from django.core.files.storage import FileSystemStorage
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from django.shortcuts import render
from beta_invite.models import User, Visitor, Profession, Education, Country, Campaign, Trade, TradeUser, Bullet, BulletType, Test, Question, Survey, Score, Evaluation
from ipware.ip import get_ip
from beta_invite import constants as cts
from beta_invite.util import email_sender
from beta_invite import text_analizer


def remove_accents(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')


def rename_filename(filename):
    """Removes accents, spaces and other chars to have a easier time later"""

    replacement = {' ': '_', '(': '_', ')': '_'}

    for my_char, replace_char in replacement.items():

        if my_char in filename:
            filename = filename.replace(my_char, replace_char)

    return remove_accents(filename)


def save_curriculum_from_request(request, user, param_name):
    """
    Saves file on machine resumes/* file system
    Args:
        request: HTTP request
        user: Object
        param_name: string, name of File on the request
    Returns: file url or None if nothing is saves.
    """

    # validate correct method and has file.
    if request.method == 'POST' and len(request.FILES) != 0 and request.FILES[param_name] is not None:

        curriculum_file = request.FILES[param_name]
        fs = FileSystemStorage()

        user_id_folder = str(user.id)
        folder = os.path.join('resumes', user_id_folder)

        file_path = os.path.join(folder, rename_filename(curriculum_file.name))

        fs.save(file_path, curriculum_file)

        # once saved it will collect the file
        subprocess.call('python3 manage.py collectstatic -v0 --noinput', shell=True)

        # at last returns the curriculum url
        return file_path

    else:
        return '#'


def index(request):
    """
    This view works for both user and business versions. It is displayed on 3 different urls: peaku.co, /business,
    /beta_invite
    :param request: can come with args "name" and "email", if not it will load the initial page.
    :return: renders a view.
    """

    return render(request, cts.HOME_VIEW_PATH)


def post_index(request):
    """
    Action taken when a form is submitted, coming from index.html
    Args:
        request: A request object.

    Returns: saves new User
    """
    # Gets information of client: such as if it is mobile
    ua_string = request.META['HTTP_USER_AGENT']
    user_agent = parse(ua_string)

    ip = get_ip(request)

    user = User(name=request.POST.get('name'),
                email=request.POST.get('email'),
                ip=ip,
                ui_version=cts.UI_VERSION,
                is_mobile=user_agent.is_mobile,)

    # Saves here to get an id
    user.save()
    user.curriculum_url = save_curriculum_from_request(request, user, 'curriculum')
    user.save()

    update_search_dictionary_on_background()

    # TODO: pay the monthly fee
    #try:
    #    email_sender.send(user, request.LANGUAGE_CODE)
    #except smtplib.SMTPRecipientsRefused:  # cannot send, possibly invalid emails
    #    pass

    return render(request, cts.SUCCESS_VIEW_PATH, {'main_message': _("Discover your true passion"),
                                                   'secondary_message': _("We search millions of jobs and find the right one for you"),
                                                   })


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


def translate_campaign(campaign, language_code):
    """
    Args:
        campaign: Object
        language_code: 'es', 'en' etc.
    Returns: Inplace object translation
    """
    if language_code == 'es':
        campaign.description = campaign.description_es
        campaign.title = campaign.title_es


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
    translate_campaign(campaign, request.LANGUAGE_CODE)

    ip = get_ip(request)
    action_url = '/beta_invite/long_form/post'
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
            translate_campaign(campaign, request.LANGUAGE_CODE)
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


def get_campaign_from_request(request):
    """Tries 2 ways to get the campaign_id, 1. on GET params, 2. on POST params.
    If nothing works outputs the default campaign."""

    campaign_id = request.GET.get('campaign_id')
    if campaign_id is None:
        campaign_id = request.POST.get('campaign_id', cts.DEFAULT_CAMPAIGN_ID)

    try:
        return Campaign.objects.get(pk=int(campaign_id))
    except ObjectDoesNotExist:
        return Campaign.objects.get(pk=cts.DEFAULT_CAMPAIGN_ID)


def get_tests_questions_dict(tests):
    return {test.id: [q.id for q in test.questions.all()] for test in tests}


def post_long_form(request):
    """
    Args:
        request: Request object
    Returns: Saves
    """
    # Gets information of client: such as if it is mobile.
    ua_string = request.META['HTTP_USER_AGENT']
    is_mobile = parse(ua_string).is_mobile
    ip = get_ip(request)

    profession_id = request.POST.get('profession')
    education_id = request.POST.get('education')
    country_id = request.POST.get('country')
    experience = request.POST.get('experience')

    campaign = get_campaign_from_request(request)

    tests = translate_tests(campaign.tests.all(), request.LANGUAGE_CODE)

    params = {'main_message': _("Discover your true passion"),
              'secondary_message': _("We search millions of jobs and find the right one for you"),
              'campaign_id': campaign.id,
              'tests': tests,
              'question_ids': get_tests_questions_dict(tests),
              }

    if profession_id is not None and education_id is not None and country_id is not None:

        profession = Profession.objects.get(pk=profession_id)
        education = Education.objects.get(pk=education_id)
        country = Country.objects.get(pk=country_id)

        user = User(name=request.POST.get('name'),
                    email=request.POST.get('email'),
                    phone=request.POST.get('phone'),
                    profession=profession,
                    education=education,
                    country=country,
                    experience=experience,
                    ip=ip,
                    ui_version=cts.UI_VERSION,
                    is_mobile=is_mobile,
                    campaign=campaign)

        # verify that the campaign exists.

        # Saves here to get an id
        user.save()
        user.curriculum_url = save_curriculum_from_request(request, user, 'curriculum')
        user.save()

        params['user_id'] = user.id

        #update_search_dictionary_on_background()

        try:
            email_body_name = 'user_signup_email_body'
            if is_mobile:
                email_body_name += '_mobile'

            email_sender.send(user, request.LANGUAGE_CODE, email_body_name, _('Welcome to PeakU'))
        except smtplib.SMTPRecipientsRefused:  # cannot send, possibly invalid emails
            pass

    else:
        # Adds the user id to the params, to be able to track answers, later on.
        user_id = request.GET.get('user_id')
        if user_id is not None:
            params['user_id'] = int(user_id)

    return render(request, cts.SUCCESS_VIEW_PATH, params)


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
    action_url = '/beta_invite/fast_job/post'
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
            translate_campaign(campaign, request.LANGUAGE_CODE)
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

    # TODO: just try it.
    #try:
    #    email_sender.send(user)
    #except smtplib.SMTPRecipientsRefused:  # cannot send, possibly invalid emails
    #    pass

    return render(request, cts.SUCCESS_VIEW_PATH, {'main_message': _("Find a job now"),
                                                   'secondary_message': _("We search millions of jobs and find the right one for you"),
                                                   })


def average_list(array):
    return sum(array)/len(array)


def get_test_result(request):
    """
    Args:
        request: HTTP object
    Returns: Either end process or invites to interview.
    """
    campaign = get_campaign_from_request(request)
    questions_dict = get_tests_questions_dict(campaign.tests.all())

    scores = []
    cut_scores = []
    for test_id, question_ids in questions_dict.items():
        total = 0
        result = 0
        cut_scores.append(Test.objects.get(pk=test_id).cut_score)
        for q_id in question_ids:

            question = Question.objects.get(pk=q_id)
            answer_text = request.POST.get('test_{}_question_{}'.format(test_id, q_id))

            survey = Survey(test_id=test_id,
                            question_id=q_id)

            user_id = request.POST.get('user_id')
            if user_id != '':
                survey.user_id = int(user_id)

            total += 1
            if question.type.code == 'SA':
                if answer_text is not None:
                    answer_id = int(answer_text)
                    survey.answer_id = answer_id
                    if answer_id in [q.id for q in Question.objects.get(pk=q_id).correct_answers.all()]:
                        result += 1
            elif question.type.code == 'OF':
                survey.text_answer = answer_text
                result += text_analizer.get_score(answer_text)
            elif question.type.code == 'MA':
                pass
                # TODO: implement multiple answers.

            survey.save()

        test_score = text_analizer.handle_division_by_zero(result, total)*100

        score = Score(test_id=test_id,
                      value=test_score)
        if user_id != '':
            score.user_id = int(user_id)
        score.save()

        scores.append(test_score)

    # simple average and percentage
    final_score = average_list(scores)
    cut_score = average_list(cut_scores)

    evaluation = Evaluation(campaign=campaign,
                            cut_score=cut_score,
                            final_score=final_score)

    evaluation.save()

    if user_id != '':
        user = User.objects.get(pk=user_id)
        user.evaluations.add(evaluation)
        user.save()

    if evaluation.passed:
        return render(request, cts.MEET_VIEW_PATH, {'main_message': _("Discover your true passion"),
                                                    'secondary_message': _("We search millions of jobs and find the right one for you"),
                                                    'campaign': campaign,
                                                    })
    else:  # doesn't pass.
        return render(request, cts.SUCCESS_VIEW_PATH, {'main_message': _("Discover your true passion"),
                                                       'secondary_message': _("We search millions of jobs and find the right one for you"),
                                                       })
