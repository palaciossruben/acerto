
import common

from dashboard.models import State
from beta_invite.models import EmailType
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
                  non_null_equal(c.user.work_area, c.campaign.work_area)]

    # Cuts top candidates because its too expensive a job filter.
    candidates = candidates[:MAX_MATCHES]
    return [c.user for c in candidates if not common.user_has_job(c.user)]


def get_top_users(campaign):

    # TODO: this feature only supports Spanish.
    search_text = campaign.get_search_text()
    search_array = search_module.get_word_array_lower_case_and_no_accents(search_text)
    users = search_module.get_matching_users(search_array)

    return simple_filter(campaign, users)


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
