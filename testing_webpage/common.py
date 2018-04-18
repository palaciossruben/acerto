from urllib.parse import urlencode, urlunparse, urlparse, parse_qsl, parse_qs

from django.core.exceptions import ObjectDoesNotExist
from ipware.ip import get_ip
import geoip2.database
from beta_invite.apps import ip_country_reader, ip_city_reader

from beta_invite.models import User, Campaign, Country, City
from beta_invite import constants as beta_cts
from dashboard.models import Candidate


CONJUNCTIONS = {'las', 'para', 'los', 'del', 'and', 'el', 'en', 'de', 'the', 'for', 'with'}
INTERVIEW_INTRO_VIDEO = './interview_intro_video.txt'
ZIGGEO_API_KEY = './ziggeo_api_key.txt'


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

    # different from None, '' and False
    if user_id:
        try:
            return User.objects.get(pk=int(user_id))
        except ObjectDoesNotExist:
            pass

    return None


def get_candidate_from_request(request):
    """Tries 2 ways to get the candidate, 1. on GET params, 2. on POST params.
    If nothing works outputs None"""

    candidate_id = request.GET.get('candidate_id')
    if candidate_id is None:
        candidate_id = request.POST.get('candidate_id')

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

    campaign_id = request.GET.get('campaign_id')
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


def get_candidate(user, campaign):

    if user and campaign:
        return Candidate.objects.get(campaign=campaign, user=user)
    else:
        return None


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


def get_city(request, country):
    """
    Gets the city by recalling it or adding new City object
    :param request: HTTP
    :param country: Country object
    :return: City Object
    """
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
