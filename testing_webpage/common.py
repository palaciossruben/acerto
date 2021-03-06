import inspect
import os
import shutil
import unicodedata
from datetime import datetime, timedelta
from urllib.parse import urlencode, urlunparse, urlparse, parse_qsl, parse_qs

import geoip2.database
import inflection
from decouple import config
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.files.storage import FileSystemStorage
from django.db.models import F
from django.db.models import Q
from django.db.transaction import atomic
from ipware.ip import get_ip

from basic_common import not_admin_user
from beta_invite import constants as beta_cts
from beta_invite.apps import ip_country_reader, ip_city_reader
from beta_invite.models import User, Campaign, Country, City, Profession, Education, EvaluationSummary, WorkArea, Gender
from business.models import BusinessUser
from dashboard.models import Candidate, State
from testing_webpage import settings

INTERVIEW_INTRO_VIDEO = './interview_intro_video.txt'
ZIGGEO_API_KEY = './ziggeo_api_key.txt'


def get_host():
    if settings.DEBUG:
        host = '//127.0.0.1:8000'
    else:
        host = 'https://peaku.co'
    return host


def remove_accents(text):
    if isinstance(text, str):
        return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    else:
        return text


def rename_filename(filename):
    """Removes accents, spaces and other chars to have a easier time later"""

    replacement = {' ': '_', '(': '_', ')': '_'}

    for my_char, replace_char in replacement.items():

        if my_char in filename:
            filename = filename.replace(my_char, replace_char)

    return remove_accents(filename)


def get_content_of_file(file_path):
    """
    Removes last '\n' if present
    Returns: String with key, or None if file not found
    """
    try:
        content = open(file_path).read()

        if not content or len(content) == 0:
            return None

        return content[:-1] if content[-1] == '\n' else content
    except FileNotFoundError:
        return None


# Change for the settings.init file
def get_ziggeo_api_key():
    return get_content_of_file(ZIGGEO_API_KEY)


def set_intro_video(new_token):
    with open(INTERVIEW_INTRO_VIDEO, 'w') as f:
        f.write(new_token)


def get_intro_video():
    return get_content_of_file(INTERVIEW_INTRO_VIDEO)


def get_user_from_request(request):
    """Tries 2 ways to get the user_id, 1. on GET params, 2. on POST params.
    If nothing works outputs None"""

    user_id = request.GET.get('user_id')
    if user_id is None:
        user_id = request.POST.get('user_id')
        if user_id is None and request.user.id is not None:
            try:
                user_id = User.objects.get(auth_user_id=request.user.id).id
            except ObjectDoesNotExist:
                user_id = None
            except MultipleObjectsReturned:
                user_id = None

    # different from None, '' and False
    if user_id:
        try:
            return User.objects.get(pk=int(user_id))
        except ObjectDoesNotExist:
            pass

    return None


def get_candidate_from_request(request):
    """Tries 3 ways to get the candidate, 1. on GET params, 2. on POST params. 3. with GET params of user and campaign
    If nothing works outputs None"""

    candidate_id = request.GET.get('candidate_id')
    if candidate_id is None:
        candidate_id = request.POST.get('candidate_id')
        if candidate_id is None:
            user_id = request.GET.get('user_id')
            campaign_id = request.GET.get('campaign_id')
            if user_id and campaign_id:
                try:
                    return Candidate.objects.get(user_id=user_id, campaign_id=campaign_id)
                except ObjectDoesNotExist:
                    return None
                except MultipleObjectsReturned:
                    return None

    # different from None, '' and False
    if candidate_id:
        try:
            return Candidate.objects.get(pk=int(candidate_id))
        except ObjectDoesNotExist:
            pass

    return None


def get_campaign_from_request(request):
    """Tries 2 ways to get the campaign_id, 1. on GET params, 2. on POST params.
    If nothing works outputs the default campaign."""

    campaign_id = request.GET.get('campaign_id', None)
    if campaign_id is None:
        campaign_id = request.POST.get('campaign_id', beta_cts.DEFAULT_CAMPAIGN_ID)

    try:
        return Campaign.objects.get(pk=int(campaign_id))
    except ObjectDoesNotExist:
        return Campaign.objects.get(pk=beta_cts.DEFAULT_CAMPAIGN_ID)


def add_params_tu_url(url, params):
    """
    Args:
        url: string
        params: dict with params
    Returns: string with url and params
    """
    url_parts = list(urlparse(url))
    query = dict(parse_qsl(url_parts[4]))
    query.update(params)

    url_parts[4] = urlencode(query)

    return urlunparse(url_parts)


def remove_params_from_url(url):
    """
    Removes the GET params from a url
    Args:
        url: string
    Returns: url without params
    """
    u = urlparse(url)
    query = parse_qs(u.query)
    query.pop('q2', None)
    u = u._replace(query=urlencode(query, True))
    return urlunparse(u)


def replace(my_list, to_remove, to_replace):
    """
    Some replacing action in a list
    :param my_list: any list
    :param to_remove: to be removed
    :param to_replace: for this other stuff
    :return: list
    """
    return [to_replace if e == to_remove else e for e in my_list]


def get_candidates(user):

    if user:
        try:
            return Candidate.objects.filter(user=user, removed=False).all()
        except ObjectDoesNotExist:
            return []
    else:
        return []


def get_candidate(user, campaign):

    if user and campaign:
        try:
            return Candidate.objects.get(campaign=campaign, user=user, removed=False)
        except ObjectDoesNotExist:
            return None
        except MultipleObjectsReturned:
            return None
    else:
        return None


def get_candidates_from_campaign(campaign):
    if campaign:
        return [c for c in Candidate.objects.filter(campaign=campaign)]
    else:
        return []


# TODO: Make method present on common.py a method of the class User. For this to happen, Candidate class has
# to be moved to testing_webpage to solve circular dependency problem.
def get_all_campaign_ids(user):
    """
    Users are unique and have multiple Candidates associated. Each one of which has 1 campaign. This method
    returns all campaigns from all Candidates associated to user.
    Returns: a list of campaign_ids where the user is a candidate.
    IMPORTANT: it gets both active or removed candidate's campaign ids.
    """
    return [candidate.campaign.id for candidate in Candidate.objects.filter(user=user)]


def get_country_with_request(request):
    """
    Returns Country object, given HTTP request,
    if address not found returns Colombia
    if country not found returns None
    :param request: HTTP
    :return: country code or None
    """

    ip = get_ip(request)

    # ip = '70.60.244.226' # US
    # ip = '191.144.0.1' # CO

    try:
        response = ip_country_reader.country(ip)
        iso_code = response.country.iso_code
    except geoip2.errors.AddressNotFoundError:
        iso_code = 'CO'  # Defaults to 'CO' if address not found

    countries = Country.objects.filter(ISO=iso_code)
    if countries:
        return [c for c in countries][0]
    else:  # defaults to English
        return None


def get_city_name_with_request(request):
    """
    Returns Country object, given HTTP request,
    if address not found returns Colombia
    if country not found returns None
    :param request: HTTP
    :return: city or None
    """

    ip = get_ip(request)

    # ip = '70.60.244.226'  # US
    # ip = '191.144.0.1'  # CO

    try:
        response = ip_city_reader.city(ip)
        name = response.city.name
        if name:
            return name
        else:
            return 'not available'  # Defaults to 'not available'
    except geoip2.errors.AddressNotFoundError:
        return 'not available'  # Defaults to 'not available'


def get_city(request):
    """
    Gets the city by recalling it or adding new City object
    :param request: HTTP
    :return: City Object
    """

    country = get_country_with_request(request)

    if settings.DEBUG:
        try:
            return City.objects.get(name='Bogotá', country=country)
        except ObjectDoesNotExist:
            pass

    city_name = get_city_name_with_request(request)

    cities = [c for c in City.objects.filter(name=city_name, country=country)]
    if len(cities) > 0:
        city = cities[0]
    else:
        city = City(name=city_name, country=country)
        city.save()

    return city


def get_language_with_ip(request):
    """
    Returns language code given a HTTP request
    :param request: HTTP
    :return: language code
    """
    country = get_country_with_request(request)
    if country:
        return country.language_code
    else:  # defaults to English
        return 'en'


def update_object(instance, params):
    for attr, value in params.items():
        setattr(instance, attr, value)
    instance.save()


def get_name_field(language_code):
    if language_code not in 'en':
        return 'name_' + language_code
    else:
        return 'name'


def get_professions(language_code):
    professions = Profession.objects.all().order_by(get_name_field(language_code))
    translate_list_of_objects(professions, language_code)
    return professions


def get_work_areas(language_code):
    work_areas = WorkArea.objects.all().order_by(get_name_field(language_code))
    translate_list_of_objects(work_areas, language_code)
    return work_areas


def get_cities():
    alias_cities = [c for c in City.objects.filter(~Q(alias=None)).all()]
    for alias_city in alias_cities:
        alias_city.name = alias_city.alias

    return sorted([c for c in City.objects.all()] + alias_cities, key=lambda c: c.name)


def get_education(language_code):
    education = Education.objects.all().order_by('level')
    translate_list_of_objects(education, language_code)
    return education


def get_countries():
    return Country.objects.all().order_by('name')


def get_genders(language_code):
    return translate_list_of_objects(Gender.objects.all(), language_code)


# TODO: Localization a las patadas
def translate_list_of_objects(objects, language_code):
    """Assigns to field name the language specific one."""
    if 'es' in language_code:
        for o in objects:
            o.name = o.name_es
    return objects


def get_object_attribute_name(key, my_object):
    """
    A standard pattern for object-attribute naming is as follows:
    '<obj_id>_<object_class_name>_<attribute_name>'
    Splits by 'object_class_name', then removes everything before it,
    then joins again to form <attribute_name>
    :param key: any string that follows the pattern mentioned above, eg: '12_question_type_id'
    :param my_object: An instance or a class eg: question of Type Question, or class Question
    :return: attribute_name, eg: type_id
    """

    if inspect.isclass(my_object):
        class_name = my_object.__name__
    else:  # instance
        class_name = my_object.__class__.__name__

    # inflection converts to snake_case
    class_name = inflection.underscore(class_name)
    class_name = '_{}_'.format(class_name)
    return class_name.join(key.split(class_name)[1:])


def get_media_path(end_path):
    return os.path.join(config('project_directory'), 'media', end_path)


def save_resource_from_request(request, my_object, param_name, folder_name, clean_directory_on_writing=False):
    """
    Saves file on machine resumes/* file system
    Args:
        request: HTTP request
        my_object: Any saved Object with a valid id.
        param_name: string, name of File on the request
        folder_name: string with name of folder
        clean_directory_on_writing: if True will clean the object_id folder each time there is a writting
    Returns: file url or None if nothing is saves.
    """

    # validate correct method and has file.
    if request.method == 'POST' and len(request.FILES) != 0 and request.FILES.get(param_name) is not None:

        my_file = request.FILES[param_name]
        fs = FileSystemStorage()

        my_object_id_folder = str(my_object.id)

        folder = os.path.join(folder_name, my_object_id_folder)

        if os.path.isdir(get_media_path(folder)) and clean_directory_on_writing:
            shutil.rmtree(get_media_path(folder))

        file_path = os.path.join(folder, rename_filename(my_file.name))

        fs.save(file_path, my_file)

        # at last returns the curriculum url
        return file_path

    else:
        return '#'


def user_has_been_recommended(user):
    """
    Returns boolean indicating if user already has a job.
    """
    candidates = Candidate.objects.filter(user=user,
                                          state__code__in=State.get_recommended_state_codes())
    return candidates.exists()


def get_recommended_candidates(campaign):
    return Candidate.objects.filter(campaign=campaign,
                                    state__code__in=State.get_recommended_state_codes(),
                                    removed=False)\
        .order_by(F('evaluation_summary__final_score').desc(nulls_last=True))


def get_relevant_candidates(campaign):
    candidates = Candidate.objects.filter(campaign=campaign,
                                          state__code__in=State.get_relevant_state_codes(),
                                          removed=False)
    return sorted(candidates, key=lambda c: c.evaluation_summary.final_score + (c.state.code == 'STC')*100 if c.evaluation_summary and c.evaluation_summary.final_score else -1, reverse=True)


def get_application_candidates(campaign):
    return Candidate.objects.filter(campaign=campaign,
                                    state__code__in=State.get_applicant_state_codes(),
                                    removed=False)\
        .order_by(F('evaluation_summary__final_score').desc(nulls_last=True))


def get_rejected_candidates(campaign):
    return Candidate.objects.filter(campaign=campaign,
                                    state__code__in=State.get_rejected_state_codes(),
                                    removed=False)\
        .order_by(F('evaluation_summary__final_score').desc(nulls_last=True))


# This methods are for the sake of speed!!!
def get_relevant_candidates_count(campaign):
    return Candidate.objects.filter(campaign=campaign,
                                    state__code__in=State.get_relevant_state_codes(),
                                    removed=False).count()


def get_application_candidates_count(campaign):
    return Candidate.objects.filter(campaign=campaign,
                                    state__code__in=State.get_applicant_state_codes(),
                                    removed=False).count()


def get_rejected_candidate_count(campaign):
    return Candidate.objects.filter(campaign=campaign,
                                    state__code__in=State.get_rejected_state_codes(),
                                    removed=False).count()


def get_recommended_candidates_count(campaign):
    return Candidate.objects.filter(campaign=campaign,
                                    state__code__in=State.get_recommended_state_codes(),
                                    removed=False).count()


def calculate_evaluation_summaries(campaign):
    """
    Gets all candidates for each BusinessState and calculates the average scores. If the candidate is missing its
    calculation it will also try doing that internally.
    """

    campaign.recommended_evaluation = EvaluationSummary.create([c.get_evaluation_summary()
                                                                for c in get_recommended_candidates(campaign)])
    campaign.relevant_evaluation = EvaluationSummary.create([c.get_evaluation_summary()
                                                             for c in get_relevant_candidates(campaign)])
    # campaign.applicant_evaluation = EvaluationSummary.create([c.get_evaluation_summary()
    #                                                          for c in get_application_candidates(campaign)])
    # campaign.rejected_evaluation = EvaluationSummary.create([c.get_evaluation_summary()
    #                                                         for c in get_rejected_candidates(campaign)])

    # LAST
    campaign.recommended_evaluation_last = EvaluationSummary.create([c.get_last_evaluation()
                                                                     for c in get_recommended_candidates(campaign)])
    campaign.relevant_evaluation_last = EvaluationSummary.create([c.get_last_evaluation()
                                                                  for c in get_relevant_candidates(campaign)])
    # campaign.applicant_evaluation_last = EvaluationSummary.create([c.get_last_evaluation()
    #                                                          for c in get_application_candidates(campaign)])
    # campaign.rejected_evaluation_last = EvaluationSummary.create([c.get_last_evaluation()
    #                                                         for c in get_rejected_candidates(campaign)])

    campaign.save()


def calculate_evaluation_summaries_with_caching(campaign):
    """
    Will only update evaluations after an hour or if the don't exist
    :param campaign:
    :return:
    """

    if campaign:
        if campaign.applicant_evaluation is not None:
            if datetime.today() - campaign.recommended_evaluation.created_at.replace(tzinfo=None) > timedelta(hours=1):
                calculate_evaluation_summaries(campaign)
            else:
                pass  # do not update... does not worth it
        else:
            calculate_evaluation_summaries(campaign)


def calculate_operational_efficiency(campaign):
    """
    Important KPI answering how difficult is to find a good candidate on late stages of process
    This percentage should as high as possible,
    otherwise to much time is spent on operation (interviews, messages, etc.)
    """
    recommended_count = get_recommended_candidates_count(campaign)
    not_that_good_count = Candidate.objects.filter(campaign=campaign, state__in=State.get_rejected_by_human_states()).count()
    total = recommended_count + not_that_good_count

    if total != 0:
        campaign.operational_efficiency = recommended_count / total
    else:
        campaign.operational_efficiency = None
    campaign.save()


def access_for_users(request, campaign, business_user):
    return not_admin_user(request) and (request.user.id != business_user.auth_user.id or campaign
                                        not in business_user.campaigns.all())


def get_business_user_with_campaign(campaign):
    """
    Given a campaign gets the business_user if it exists, else None
    :return: business_user or None
    """
    try:
        return BusinessUser.objects.get(campaigns__id=campaign.pk)
    except ObjectDoesNotExist:
        return None
    except MultipleObjectsReturned:
        return BusinessUser.objects.filter(campaigns__id=campaign.pk).all()[0]


@atomic
def bulk_save(objects):
    for item in objects:
        item.save()
