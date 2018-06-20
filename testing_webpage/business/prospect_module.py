
import common

from dashboard.models import State
from beta_invite.models import EmailType
from testing_webpage.models import CandidatePendingEmail
from business import search_module
from dashboard.models import Candidate
from match import model, clustering
from match.pickle_models import pickle_handler


MAX_MATCHES = 60


# TODO: deprecated, now all users are all distinct.
def get_distinct_users(users):
    """
    Args:
        users: Users QuerySet.
    Returns: Only sends email ones, to a given email.
    """
    return users.order_by().distinct('email')


def filter_users_with_job(users):
    """
    Removes from list users who got a job on any campaign.
    Args:
        users: list of users.
    Returns: list of users
    """
    excluded_users = []
    for u in users:
        candidate = Candidate.objects.filter(user=u)
        for c in candidate:
            if c.state.code == "GTJ":
                excluded_users.append(u)

    return [x for x in users if x not in excluded_users]


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


def cluster_filter(candidates):
    clusters, candidates = clustering.predict_cluster(candidates)
    return [candidate for c, candidate in zip(clusters, candidates) if c in pickle_handler.load_selected_clusters()]


def non_null_equal(a, b):
    if a is not None and b is not None:
        return a == b
    return False


def get_desc_sorted_iterator(candidates_rank):
    return reversed(sorted([(c, rank) for c, rank in candidates_rank], key=lambda t: t[1]))


def rank(campaign, users):
    """
    Sorts according to given criteria:
    1. city
    2. country
    3. work area
    4. prediction
    :param campaign:
    :param users:
    :return:
    """
    candidates = [Candidate(user=u, campaign=campaign, pk=1) for u in users]

    candidates_rank = [(c, non_null_equal(c.user.city, c.campaign.city) +
                           non_null_equal(c.user.country, c.campaign.country) +
                           non_null_equal(c.user.work_area, c.campaign.work_area)) for c in candidates]

    candidates_rank = [(c, rank) for c, rank in get_desc_sorted_iterator(candidates_rank)]

    # Cuts top candidates because its too expensive a job filter.
    candidates_rank = candidates_rank[:MAX_MATCHES]
    candidates_rank = [(c, rank) for c, rank in candidates_rank if not common.user_has_job(c.user)]

    return [c.user for c, rank in get_desc_sorted_iterator(candidates_rank)]


def enough_info(candidate):
    """
    Needs a minimum of information in order to take it into account.
    :param candidate: Object Candidate
    :return:
    """
    if candidate.user and candidate.campaign and (candidate.user.work_area
                                                  or candidate.user.profession
                                                  or candidate.campaign.work_area
                                                  or candidate.campaign.profession):
        return False
    return True


def get_weight_with_business_rules(candidate, campaign):

    if not enough_info(candidate):
        return -1000

    # Gives 0 weight, the lowest weight that can be shown
    if campaign.work_area is None:
        return 0

    if candidate.user and non_null_equal(candidate.user.work_area, campaign.work_area):
        return 8

    if candidate.user and candidate.user.work_area and campaign.work_area\
            and non_null_equal(candidate.user.work_area.type, campaign.work_area.type):
        return 7

    if candidate.user and non_null_equal(candidate.user.profession, campaign.profession):
        return 6

    if candidate.user and candidate.user.profession and campaign.profession\
            and non_null_equal(candidate.user.profession.type, campaign.profession.type):
        return 5

    if candidate.campaign and non_null_equal(candidate.campaign.work_area, campaign.work_area):
        return 4

    if candidate.campaign and candidate.campaign.work_area and campaign.work_area\
            and non_null_equal(candidate.campaign.work_area.type, campaign.work_area.type):
        return 3

    if candidate.campaign and non_null_equal(candidate.campaign.profession, campaign.profession):
        return 2

    if candidate.campaign and candidate.campaign.profession and campaign.profession\
            and non_null_equal(candidate.campaign.profession.type, campaign.profession.type):
        return 1

    # if non of the above it will filter the stuff
    return -1000


def get_weight(candidate, campaign):
    """
    Negative weights indicate filtering.
    :param candidate: Candidate
    :param campaign:
    :return:
    """

    w = get_weight_with_business_rules(candidate, campaign)

    if non_null_equal(candidate.user.city, candidate.campaign.city):
        w += 4

    if non_null_equal(candidate.user.country, candidate.campaign.country):
        w += 2

    return w


def rank2(campaign, users):
    """
    1. Create and Cut top candidates because its too expensive.
    2. get weights
    3. filter negative weights
    4. filter candidates with job
    5. sort candidates, desc
    """

    candidates = [Candidate(user=u, campaign=campaign, pk=1) for u in users][:MAX_MATCHES]
    candidates_rank = [(c, get_weight(c, campaign)) for c in candidates]
    candidates_rank = [(c, r) for c, r in candidates_rank if r >= 0]
    candidates_rank = [(c, rank) for c, rank in candidates_rank if not common.user_has_job(c.user)]

    return [c.user for c, rank in get_desc_sorted_iterator(candidates_rank)]


def get_top_users(campaign):

    # TODO: this feature only supports Spanish.
    search_text = campaign.get_search_text()
    search_array = search_module.get_word_array_lower_case_and_no_accents(search_text)
    users = search_module.get_matching_users(search_array)

    return rank2(campaign, users)


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

            candidates.append(candidate)
            candidate.save()

    return candidates
