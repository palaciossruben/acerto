
import common

from dashboard.models import State
from beta_invite.models import EmailType
from testing_webpage.models import PendingEmail
from business import search_module
from dashboard.models import Candidate


NUMBER_OF_MATCHES = 10


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
        PendingEmail.add_to_queue(candidates=candidate,
                                  language_code=candidate.user.language_code,
                                  body_input='user_job_match_email_body',
                                  subject=translate_email_job_match_subject(candidate),
                                  override_dict={'campaign_url': candidate.campaign.get_url()},
                                  email_type=email_type)


def get_top_users(campaign):
    # TODO: this feature only supports Spanish.
    search_text = campaign.get_search_text()
    search_array = search_module.get_word_array_lower_case_and_no_accents(search_text)
    users = search_module.get_matching_users(search_array)

    top_users = [u for u in users][:NUMBER_OF_MATCHES]
    return filter_users_with_job(top_users)


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
