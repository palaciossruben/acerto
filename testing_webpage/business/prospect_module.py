
import urllib.parse
from django.db.models import Q
import requests
from decouple import config

import common

from dashboard.models import State
from beta_invite.models import EmailType, User, SearchLog
from testing_webpage.models import CandidatePendingEmail
from business import search_module
from dashboard.models import Candidate

MAX_MATCHES = 40


def translate_email_job_match_subject(candidate):
    """
    Default will be in spanish
    Args:
        candidate: Candidate object
    Returns: translated subject
    """
    if candidate.user.language_code is None or candidate.user.language_code == 'es':
        return 'Vacante abierta para {campaign}'.format(campaign=candidate.campaign.title_es)
    else:
        return 'Open position for {campaign}'.format(campaign=candidate.campaign.title)


def send_mails(candidate_prospects):
    """
    Sends email for each prospect 
    :param candidate_prospects: List of candidates
    :return: None
    """
    email_type = EmailType.objects.get(name='job_match')
    for candidate in candidate_prospects:
        CandidatePendingEmail.add_to_queue(candidates=candidate,
                                           language_code=candidate.user.language_code,
                                           body_input='user_job_match_email_body',
                                           subject=translate_email_job_match_subject(candidate),
                                           override_dict={'campaign_url': candidate.campaign.get_url()},
                                           email_type=email_type)


def non_null_equal(a, b):
    if a is not None and b is not None:
        return a == b
    return False


def non_null_lte(a, b):
    if a is not None and b is not None:
        return a <= b
    return False


def non_null_gte(a, b):
    if a is not None and b is not None:
        return a >= b
    return False


def simple_filter(campaign, users):
    """
    Filters by:
    1. city
    2. work area
    3. not having job
    :param campaign: a Campaign object
    :param users: list of User objects
    :return: list of candidates
    """
    candidates = [Candidate(user=u, campaign=campaign, pk=1) for u in users]

    candidates = [c for c in candidates if non_null_equal(c.user.city, c.campaign.city) and
                  non_null_equal(c.user.work_area, c.campaign.work_area) and
                  non_null_lte(campaign.get_very_low_salary(), c.user.salary) and
                  non_null_gte(campaign.get_very_high_salary(), c.user.salary)]

    # Cuts top candidates because its too expensive a job filter.
    candidates = candidates[:MAX_MATCHES]
    return [c.user for c in candidates if not common.user_has_been_recommended(c.user)]


def get_users_from_es(search_array):
    """
    es=elastic_search
    :param search_array: array of search words
    :return: Users
    """

    search_text = '%20'.join(search_array)
    try:
        r = requests.get(urllib.parse.urljoin(config('elastic_search_host'), '/users/_search?q={}'.format(search_text)))

        if str(r.status_code)[0] == 2:
            return User.objects.filter(pk__in=[u['_id'] for u in r.json()['hits']['hits']]).all()
        else:
            return []
    except:  # TODO: fix, WTF: there are connections errors not caught
        return []


def get_users_from_tests(campaign):
    """
    An additional source of candidates are the ones who both pass the simple filter conditions and
    pass all the tests that the campaign is asking in a cognitive and technical aspect.
    :param campaign: Campaign
    :return: users
    """
    campaign_tests = [t for t in campaign.tests.all() if t.type.code in ['C', 'T']]

    # implicit implementation of the simple filter.
    candidates = Candidate.objects.filter(~Q(state__code__in=State.get_recommended_states()),
                                          user__work_area=campaign.work_area,
                                          user__city=campaign.city,
                                          user__salary__gte=campaign.get_very_low_salary(),
                                          user__salary__lte=campaign.get_very_high_salary())

    # TODO: missing complementary tests from the same user in different candidates
    # example:
    # campaign_tests = [1, 2, 3]
    # candidate1.tests = [1, 2]
    # candidate2.tests = [3]
    # True = candidate1.user == candidate2.user

    prospects = []
    for c in candidates:
        last_evaluation = c.get_last_evaluation()
        if last_evaluation:
            passing_tests = [s.test for s in last_evaluation.scores.all() if s.passed]
            if all([t in passing_tests for t in campaign_tests]):
                prospects.append(c)

    return [c.user for c in prospects]


def get_top_users(campaign):

    # TODO: this feature only supports Spanish.
    search_text = campaign.get_search_text()
    search_array = search_module.get_word_array_lower_case_and_no_accents(search_text)
    search_array += search_module.add_related_words(search_array)

    search_log = SearchLog()
    search_log.save()
    search_log.campaign = campaign

    # Tests
    users_tests = get_users_from_tests(campaign)
    search_log.users_from_tests.add(*users_tests)
    users = users_tests

    # Search
    #users_search = search_module.get_matching_users(search_array)
    #search_log.users_from_search.add(*users_search)
    #users += users_search

    # ES
    users_es = get_users_from_es(search_array)
    search_log.users_from_es.add(*users_es)
    users += users_es

    # ALL
    search_log.all_users.add(*users)

    # FILTERS
    candidates = [Candidate(user=u, campaign=campaign, pk=1) for u in users]

    candidates = [c for c in candidates if non_null_equal(c.user.city, c.campaign.city)]
    search_log.after_city_filter.add(*[c.user for c in candidates])

    # Work Area Segment
    candidates = [c for c in candidates if non_null_equal(c.user.get_work_area_segment(), c.campaign.get_work_area_segment())]
    search_log.after_work_area_filter.add(*[c.user for c in candidates])

    candidates = [c for c in candidates if non_null_lte(campaign.get_very_low_salary(), c.user.salary) and
                  non_null_gte(campaign.get_very_high_salary(), c.user.salary)]
    search_log.after_salary_filter.add(*[c.user for c in candidates])

    # BACK TO USER
    users = [c.user for c in candidates]

    # Cuts top candidates first, because its too expensive a job filter.
    users = users[:MAX_MATCHES]
    search_log.after_cap_filter.add(*users)

    users = [u for u in users if not common.user_has_been_recommended(u)]
    search_log.after_recommended_filter.add(*users)

    users = search_module.remove_duplicates(users)
    search_log.after_duplicates_filter.add(*users)

    search_log.save()
    return users


def get_candidates(campaign):
    """
    Args:
        campaign: obj
    Returns: Creates a list of prospect users on the DB. And sends all ot them an email.
    """

    top_users = get_top_users(campaign)

    candidates = []
    for user in top_users:

        # only users who are not on the campaign will be added to the mail
        if campaign.id not in common.get_all_campaign_ids(user):

            candidate = Candidate(campaign=campaign, user=user, state=State.objects.get(code='P'))

            # TODO: adds tests
            #candidate.pass_tests()

            candidates.append(candidate)
            candidate.save()

    return candidates
