from urllib.parse import urlencode, urlunparse, urlparse, parse_qsl, parse_qs

from django.core.exceptions import ObjectDoesNotExist

from beta_invite.models import User, Campaign
from beta_invite import constants as beta_cts
from dashboard.models import Candidate


CONJUNCTIONS = {'las', 'para', 'los', 'del', 'and', 'el', 'en', 'de'}
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
def get_campaigns(user):
    """
    Users are unique and have multiple Candidates associated. Each one of which has 1 campaign. This method
    returns all campaigns from all Candidates associated to user.
    Returns: a list of campaigns where the user is a candidate.
    """
    return [candidate.campaign for candidate in Candidate.objects.filter(user=user)]
