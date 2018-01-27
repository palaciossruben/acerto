
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


def translate_email_job_match_subject(user, campaign):
    """
    Default will be in spanish
    Args:
        user: User object
    Returns: translated subject
    """
    if user.language_code is None or user.language_code == 'es':
        return 'Vacante abierta para {campaign}'.format(campaign=campaign.title_es)
    else:
        return 'Open position for {campaign}'.format(campaign=campaign.title)


def create_prospect_users_and_send_emails(campaign):
    """
    Args:
        campaign: obj
    Returns: Creates a list of prospect users on the DB. And sends all ot them an email.
    """

    email_type = EmailType.objects.get(name='job_match')

    # TODO: this feature only supports Spanish.
    search_text = search_module.with_lower_case_and_no_accents(campaign.title_es)
    users = search_module.get_matching_users(search_phrase=search_text,
                                             word_user_path='subscribe/word_user_dictionary.p')

    users = filter_users_with_job(users)
    top_users = [u for u in users][:NUMBER_OF_MATCHES]

    for user in top_users:

        # only users who are not on the campaign will be added to the mail
        if campaign.id not in common.get_all_campaign_ids(user):

            candidate = Candidate(campaign=campaign, user=user, state=State.objects.get(code='P'))
            candidate.save()

            PendingEmail.add_to_queue(candidates=candidate,
                                      language_code=candidate.user.language_code,
                                      body_input='user_job_match_email_body',
                                      subject=translate_email_job_match_subject(user, campaign),
                                      override_dict={'campaign_url': campaign.get_url()},
                                      email_type=email_type)
