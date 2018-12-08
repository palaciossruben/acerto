
import urllib.parse

import requests
from decouple import config
from django.db.models import Q
from raven import Client

import common
from beta_invite.models import EmailType, User, SearchLog
from business import search_module
from common import bulk_save
from dashboard.models import Candidate
from dashboard.models import State
from testing_webpage.models import CandidatePendingEmail

MAX_MATCHES = 40
MAX_MORE_USERS = 200
SENTRY_CLIENT = Client(config('sentry_dsn'))


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


def get_user_ids_from_es(search_array):
    """
    es=elastic_search
    :param search_array: array of search words
    :return: Users
    """

    # TODO: can search be improved?
    # 1. taking different weights for different terms
    # 2. adding related terms
    # 3. more people on original search
    # 4. using elasticsearch DSL????
    # 5. including job description
    # 6. adding back the tests stuff -> has to correct for ignoring requisites!
    # 7. return more results size=1000?
    # 8. return only the id, for less json parsing
    # 9. adds city to the elastic search filter, rather than having it in python (gains speed a num results)

    search_text = '+'.join(search_array)
    #search_text = ' '.join(search_array)

    try:

        #url = urllib.parse.urljoin(config('elastic_search_host'), '/users/_search')
        url = urllib.parse.urljoin(config('elastic_search_host'), '/users/_search?q={}'.format(search_text))
        print(url)
        my_json = {
            "_source": ["pk"],
            "size": 2000,
            #"query": {
            #    "bool": {
            #        "must": [
            #            {"match": {"_all": search_text}}
            #        ]#,
                    #"filter": [
                    #    {"term": {"city_id": campaign.city_id}}
                    #]#,
                    #"terms_set": {
                    #    "work_area_id": {
                    #        {"term": [w.pk for w in campaign.get_work_area_segment().get_work_areas()]}
                    #    }
                    #}
            #    },
            #},
        }
        #print(my_json)

        r = requests.get(url, json=my_json)
        #print(r.status_code)
        #print(r.json())

        #r = requests.post(url, data=data)

        if str(r.status_code)[0] == '2':
            return [u['_id'] for u in r.json()['hits']['hits']]
        else:
            return []
    except Exception as e:
        SENTRY_CLIENT.captureException()
        raise e


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


def get_top_users_with_log(campaign):
    """
    This function is slow but has a amazing log of what is happening with the filter. Very helpful to understand
    prospects, but extremly slow...
    :param campaign:
    :return:
    """

    # TODO: this feature only supports Spanish.
    search_text = campaign.get_search_text()
    search_array = search_module.get_word_array_lower_case_and_no_accents(search_text)
    #search_array += search_module.add_related_words(search_array)

    search_log = SearchLog()
    search_log.save()
    search_log.campaign = campaign

    # Tests
    #users_tests = get_users_from_tests(campaign)
    #search_log.users_from_tests.add(*users_tests)
    #users = users_tests
    users = []

    # Traditional Search: hard to scale
    #users_search = search_module.get_matching_users(search_array)
    #search_log.users_from_search.add(*users_search)
    #users += users_search

    # ES
    users_es = User.objects.filter(pk__in=get_user_ids_from_es(search_array))
    search_log.users_from_es.add(*users_es)
    users += users_es

    # ALL
    search_log.all_users.add(*users)

    # FILTERS
    candidates = [Candidate(user=u, campaign=campaign, pk=1) for u in users]

    # CITY FILTER
    candidates = [c for c in candidates if non_null_equal(c.user.city, c.campaign.city)]
    search_log.after_city_filter.add(*[c.user for c in candidates])

    # WORK AREA SEGMENT FILTER
    candidates = [c for c in candidates if non_null_equal(c.user.get_work_area_segment(), campaign.get_work_area_segment())]
    search_log.after_work_area_filter.add(*[c.user for c in candidates])

    # SALARY FILTER
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


def get_top_users_fast(campaign):
    """
    This function is fast but is a black box as it has no log of each filter (see: get_top_users_with_log()).
    This is for production and speed.
    :param campaign:
    :return:
    """

    # TODO: this feature only supports Spanish.
    search_text = campaign.get_search_text()
    search_array = search_module.get_word_array_lower_case_and_no_accents(search_text)

    # Gets the newest fit users, as those are likely to still be looking for a job...
    users = User.objects.filter(~Q(city_id=None),
                                ~Q(work_area=None),
                                ~Q(salary=None),
                                city_id=campaign.city_id,
                                salary__gte=campaign.get_very_low_salary(),
                                salary__lte=campaign.get_very_high_salary(),
                                work_area__segment_id=campaign.get_work_area_segment().id,
                                pk__in=get_user_ids_from_es(search_array),
                                ).order_by('-id')[:MAX_MATCHES]

    users = [u for u in users if not common.user_has_been_recommended(u)]

    return users


def add_candidates_to_campaign(campaign, users, state_code):

    state = State.objects.get(code=state_code)
    candidates = Candidate.objects.bulk_create([Candidate(campaign=campaign, user=u, state=state) for u in users])
    bulk_save(candidates)
    return candidates


    #candidates = []
    #for user in top_users:

        # only users who are not on the campaign will be added to the mail
        #if campaign.id not in common.get_all_campaign_ids(user):
    #    candidate = Candidate(campaign=campaign, user=user, state=State.objects.get(code='P'))
    #    candidates.append(candidate)
    #    candidate.save()



def get_more_users(campaign):

    # Gets the newest fit users, as those are likely to still be looking for a job...
    users = User.objects.filter(~Q(city_id=None),
                                ~Q(work_area=None),
                                ~Q(salary=None),
                                city_id=campaign.city_id,
                                salary__gte=campaign.get_very_low_salary(),
                                salary__lte=campaign.get_very_high_salary(),
                                work_area__segment_id=campaign.get_work_area_segment().id,
                                ).order_by('-id')[:MAX_MORE_USERS]

    return {u for u in users if not common.user_has_been_recommended(u)}


def get_candidates(campaign):
    """
    Args:
        campaign: obj
    Returns: Creates a list of unique prospect users. The top ones are added to the DB and shown as prospects,
    the other ones are only invited to apply
    """

    # Top candidates have the best match will be added to the campaign
    top_users = get_top_users_fast(campaign)
    top_candidates = add_candidates_to_campaign(campaign, top_users, 'P')

    # other candidates will receive a cordial invitation only...
    more_users = get_more_users(campaign).difference({t for t in top_users})
    more_candidates = add_candidates_to_campaign(campaign, more_users, 'PP')

    return top_candidates + more_candidates


def remove_html(s):
    tags = ['div', 'em', 'br', 'p', 'strong']

    for t in tags:
        s = s.replace('<{}>'.format(t), '')
        s = s.replace('</{}>'.format(t), '')
    return s
