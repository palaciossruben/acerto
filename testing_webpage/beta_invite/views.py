import os
import io
import wave
from scipy.io import wavfile

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from ipware.ip import get_ip
from user_agents import parse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_exempt
from decouple import config as CONFIG
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

from datetime import datetime
import common
from beta_invite import constants as cts
from beta_invite import test_module, new_user_module
from beta_invite.models import User, Visitor, Campaign, BulletType, City, Question, Experience, EducationExperience, School, Company
from dashboard.models import Candidate
from business.custom_user_creation_form import CustomUserCreationForm


def get_drop_down_values(language_code):
    """
    Gets lists of drop down values for several different fields.
    Args:
        language_code: 2 digit code (eg. 'es')
    Returns: A tuple containing (Countries, Education, Professions)
    """

    countries = common.get_countries()
    cities = common.get_cities()

    professions = common.get_professions(language_code)
    work_areas = common.get_work_areas(language_code)
    education = common.get_education(language_code)
    genders = common.get_genders(language_code)
    # TODO: add new drop down here

    return countries, cities, education, professions, work_areas, genders


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


def get_index_params(request):

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

    if campaign.image is None:
        campaign.image = "default"
        campaign.save()

    param_dict = {'job_title': campaign.title,
                  'perks': translate_bullets(perks, request.LANGUAGE_CODE),
                  'requirements': translate_bullets(requirements, request.LANGUAGE_CODE),
                  'is_desktop': is_desktop,
                  'work_areas': common.get_work_areas(request.LANGUAGE_CODE),
                  'cities': common.get_cities(),
                  'default_city': common.get_city(request),
                  'image': campaign.image}

    if campaign_id is not None:
        param_dict['campaign_id'] = int(campaign_id)
        try:
            campaign = Campaign.objects.get(pk=int(campaign_id))
            campaign.translate(request.LANGUAGE_CODE)
            # if campaign exists send it.
            param_dict['campaign'] = campaign
        except ObjectDoesNotExist:
            pass

    return param_dict


def index(request):
    """
    will render a form to input user data.
    """
    return render(request, cts.INDEX_VIEW_PATH, get_index_params(request))


# TODO: refactor with the other method of same name in business/views
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


def register(request):
    """
    Args:
        request: Request object
    Returns: Saves or updates the User, now it will not be creating new user objects for the same email.
    """

    signup_form = CustomUserCreationForm(request.POST)

    if signup_form.is_valid():

        # Gets information of client: such as if it is mobile.
        is_mobile = parse(request.META['HTTP_USER_AGENT']).is_mobile

        email = request.POST.get('username')
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        city_id = request.POST.get('city_id')
        work_area_id = request.POST.get('work_area_id')

        politics_accepted = request.POST.get('politics')
        if politics_accepted:
            politics = True
        else:
            politics = False
        campaign = common.get_campaign_from_request(request)

        # Validates all fields
        if campaign and name and phone and (email or not campaign.has_email):

            country = common.get_country_with_request(request)

            user_params = {'name': name,
                           'email': email,
                           'phone': phone,
                           'work_area_id': work_area_id,
                           'country': country,
                           'city': City.objects.get(pk=city_id),
                           'ip': get_ip(request),
                           'is_mobile': is_mobile,
                           'language_code': request.LANGUAGE_CODE,
                           'politics': politics}

            user = new_user_module.user_if_exists(email, phone, campaign)
            if user:
                user = new_user_module.update_user(campaign, user, user_params, request, signup_form=signup_form)
            else:
                user = new_user_module.create_user(campaign, user_params, request, is_mobile, signup_form=signup_form)

            return redirect('/servicio-de-empleo/pruebas?campaign_id={campaign_id}&user_id={user_id}'.format(campaign_id=campaign.id, user_id=user.id))
        else:
            return HttpResponseBadRequest('<h1>HTTP CODE 400: Client sent bad request with missing params</h1>')

    else:
        error_message = get_first_error_message(signup_form)
        params_dict = get_index_params(request)
        params_dict['error_message'] = error_message
        return render(request, cts.INDEX_VIEW_PATH, params_dict)


def apply(request):
    """
    When the user is logged in and applies to a second campaign
    :return:
    """

    user = User.get_user_from_request(request)
    campaign = common.get_campaign_from_request(request)

    candidate = new_user_module.candidate_if_exists(campaign, user)
    if not candidate:
        Candidate(campaign=campaign, user=user).save()

    return redirect('/servicio-de-empleo/pruebas?campaign_id={campaign_id}&user_id={user_id}'.format(
        campaign_id=campaign.id,
        user_id=user.id))


def tests(request):

    """
    Receives either GET or POST user and campaign ids.
    :param request: HTTP
    :return: renders tests.
    """

    campaign = common.get_campaign_from_request(request)
    user = common.get_user_from_request(request)
    candidate = common.get_candidate(user, campaign)

    tests = translate_tests(test_module.get_missing_tests(candidate, campaign), request.LANGUAGE_CODE)

    end_point_params = {'campaign_id': campaign.id,
                        'tests': tests}

    if not candidate:
        return redirect('/servicio-de-empleo?campaign_id={}'.format(campaign.id))
    if user is not None:
        end_point_params['user_id'] = int(user.id)  # Adds the user id to the params, to be able to track answers, later

    if tests:
        return render(request, cts.TESTS_VIEW_PATH, end_point_params)
    else:
        return redirect('/servicio-de-empleo/additional_info?candidate_id={candidate_id}'.format(candidate_id=candidate.pk))


def simple_login_and_user(login_form, request):
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

    return User.objects.get(auth_user=auth_user)


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

        try:
            user = simple_login_and_user(login_form, request)
        except ObjectDoesNotExist:
            # TODO: how to reload the exact campaign and at the same time pass on the error_message?
            return redirect('/trabajos')

        segment_code = user.get_work_area_segment_code()
        if segment_code:
            return redirect('/trabajos?segment_code={}'.format(segment_code))
        else:
            return redirect('/trabajos')

    else:
        error_message = get_first_error_message(login_form)
        # TODO: how to reload the exact page and at the same time pass on the error_message?
        return redirect('/trabajos')


def get_test_result(request):
    """
    Args:
        request: HTTP object
    Returns: Either end process or invites to interview.
    """

    campaign = common.get_campaign_from_request(request)
    user = common.get_user_from_request(request)
    user_id = user.id if user else None
    if not user:
        return redirect('/servicio-de-empleo?campaign_id={campaign_id}'.format(campaign_id=campaign.id))

    candidate = common.get_candidate(user, campaign)
    high_scores = test_module.get_high_scores(candidate, campaign)

    questions_dict = test_module.get_tests_questions_dict(test_module.get_missing_tests(candidate,
                                                                                        campaign,
                                                                                        high_scores=high_scores))
    missing_scores = test_module.get_scores(campaign, user_id, questions_dict, request)

    all_scores = missing_scores + high_scores

    test_module.get_evaluation(all_scores, candidate)

    # once it has the evaluation will update the canonical user scores
    test_module.update_scores_of_candidate(candidate)

    # probably a new comer
    if candidate.user.gender is None:
        return redirect(
            '/servicio-de-empleo/additional_info?candidate_id={candidate_id}'.format(candidate_id=candidate.pk))
    else:
        # will no longer bother user with additional info
        if candidate is not None:
            return redirect('/servicio-de-empleo/active_campaigns?candidate_id={}'.format(candidate.id))
        else:
            return redirect('/servicio-de-empleo/active_campaigns')


def additional_info(request):
    candidate = common.get_candidate_from_request(request)

    param_dict = dict()
    countries, cities, education, professions, work_areas, genders = get_drop_down_values(request.LANGUAGE_CODE)
    # Dictionary parameters
    param_dict['candidate'] = candidate
    param_dict['genders'] = genders
    param_dict['work_areas'] = work_areas
    param_dict['education'] = education
    param_dict['professions'] = professions
    param_dict['countries'] = countries
    param_dict['cities'] = cities
    param_dict['candidate'] = candidate

    return render(request, cts.ADDITIONAL_INFO_VIEW_PATH, param_dict)


def get_int_param(request, request_param):
    try:
        return int(request.POST.get(request_param))
    except ValueError:
        return None


def get_school(school_name):
    try:
        return School.objects.get(name=school_name)
    except ObjectDoesNotExist:
        school = School(name=school_name)
        school.save()
        return school


def update_education_experience(request, school_name, candidate):

    user = User.objects.get(pk=candidate.user.pk)
    order = int(request.POST.get('order'))

    try:
        study = EducationExperience.objects.get(order=order, user=user)
        study.school = get_school(school_name)
        study.profession_id = get_int_param(request, 'profession_id')
        study.education_id = get_int_param(request, 'education_id')
        study.save()

    except ObjectDoesNotExist:

        study = EducationExperience(order=order,
                                    user=user,
                                    school=get_school(school_name),
                                    profession_id=get_int_param(request, 'profession_id'),
                                    education_id=get_int_param(request, 'education_id'))
        study.save()
        user.education_experiences.add(study)
        user.save()


def get_company(company_name):
    try:
        return Company.objects.get(name=company_name)

    except ObjectDoesNotExist:
        company = Company(name=company_name)
        company.save()
        return company


def parse_date(date_string):
    split_list = date_string.split('-')
    if len(split_list) == 2:
        try:
            return datetime(year=int(split_list[0]), month=int(split_list[1]), day=1)
        except ValueError:
            return None
    else:
        return None


def update_work_experiences(request, company_name, candidate):

    user = User.objects.get(pk=candidate.user.pk)
    order = int(request.POST.get('order'))
    present = request.POST.get('present')
    start = parse_date(request.POST.get('start_date'))
    if present:
        finish = datetime.today()
    else:
        finish = parse_date(request.POST.get('finish_date'))

    try:
        work_experience = Experience.objects.get(order=order, user=user)
        work_experience.company = get_company(company_name)
        work_experience.role = request.POST.get('role')
        work_experience.highlight = request.POST.get('highlight')
        work_experience.start = start
        work_experience.finish = finish
        work_experience.order = order
        work_experience.save()

    except ObjectDoesNotExist:  # when it has to create the object from scratch

        work_experience = Experience(company=get_company(company_name),
                                     role=request.POST.get('role'),
                                     highlight=request.POST.get('highlight'),
                                     start=start,
                                     finish=finish,
                                     order=order)
        work_experience.save()
        user.experiences.add(work_experience)
        user.save()


def save_partial_additional_info(request):

    if request.method == 'POST':
        candidate = common.get_candidate_from_request(request)
        new_user_module.update_user_with_request(request, candidate.user)
        school_name = request.POST.get('school')
        company_name = request.POST.get('company_name')

        if school_name:
            update_education_experience(request, school_name, candidate)

        if company_name:
            update_work_experiences(request, company_name, candidate)

        return HttpResponse('')
    else:
        return HttpResponseBadRequest('<h1>HTTP CODE 400: Client sent bad request with missing params</h1>')


def active_campaigns(request):

    candidate = common.get_candidate_from_request(request)

    if candidate is not None:

        new_user_module.update_user(candidate.campaign, candidate.user, {}, request)

        last_evaluation = candidate.get_last_evaluation()
        if last_evaluation:
            test_module.update_scores(last_evaluation, last_evaluation.scores.all())

            # Uses ML to send to STC state!!! 100% automation reached?
            test_module.classify_evaluation_and_change_state(candidate,
                                                             use_machine_learning=True,
                                                             success_state='STC',
                                                             fail_state=candidate.state.code)

    # TODO: add salary and city filter
    if candidate and candidate.user.get_work_area_segment_code():
        return redirect('/trabajos?segment_code={}'.format(candidate.user.get_work_area_segment_code()))
    else:
        return redirect('/trabajos')


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

    user = common.get_user_from_request(request)

    if user and user.id:
        user = User.objects.get(pk=int(user.id))
        new_user_module.update_resource(request, user, 'curriculum_url', 'resumes')

    return redirect('/trabajos')


def security_politics(request):
    return render(request, cts.SECURITY_POLITICS_VIEW_PATH)


@csrf_exempt
def upload_audio_file(request):
    campaign = common.get_campaign_from_request(request)
    user = common.get_user_from_request(request)
    question = Question.objects.get(pk=request.POST.get('question_id'))
    test_id = request.POST.get('test_id')

    audio_path = common.save_resource_from_request(request, question, 'audio', 'audio', clean_directory_on_writing=True)

    try:
        transcript = run_google_speech(audio_path)
        survey = test_module.add_survey_to_candidate(campaign, test_id, question, user.id, transcript)

        if audio_path != '#':
            survey.audio_path = audio_path
            survey.save()
    except Exception as e:
        print(e)
        raise e

    return HttpResponse(200)


def describe_wav(filename):
    with wave.open(filename, "rb") as wave_file:
        sample_rate = wave_file.getframerate()
        num_channels = wave_file.getnchannels()
        print('sample rate is: {}, channels: {}'.format(sample_rate, num_channels))
        return sample_rate, num_channels


def run_google_speech(filename):

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(CONFIG('project_directory'), 'testing_webpage', 'google_cloud_speech_key.json')
    client = speech.SpeechClient()

    # The name of the audio file to transcribe
    filename = common.get_media_path(filename)

    # TODO: remove?
    """
    test_module.down_sample_wave(filename,
                                 filename,
                                 inrate=sample_rate,
                                 outrate=ideal_sample_rate,
                                 inchannels=num_channels,
                                 outchannels=1)


    """

    """
    import librosa
    audio_time_series, _ = librosa.load(filename, sr=None)
    audio_time_series = librosa.core.resample(audio_time_series,
                                              orig_sr=sample_rate,
                                              target_sr=ideal_sample_rate)

    filename = filename + '.wav'
    librosa.output.write_wav(filename, audio_time_series, ideal_sample_rate)
    """

    # With scipy
    """
    print('BEFORE:')
    in_rate, _ = describe_wav(filename)

    ds = test_module.DownSample(in_rate=in_rate, out_rate=ideal_sample_rate)
    opens = ds.open_file(filename)
    if opens:
        ds.resample(filename)
    """

    """
    freq, audio = wavfile.read(filename)

    print(audio)
    print(freq)

    wavfile.write(filename, 16000, audio)
    """

    print('AFTER:')
    describe_wav(filename)

    # Loads the audio into memory
    with io.open(filename, 'rb') as audio_file:
        content = audio_file.read()
        audio = types.RecognitionAudio(content=content)

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code='es-CO')

    # Detects speech in the audio file
    response = client.recognize(config, audio)

    for result in response.results:
        print('Transcript: {}'.format(result.alternatives[0].transcript))

    return response.results[0].alternatives[0].transcript
