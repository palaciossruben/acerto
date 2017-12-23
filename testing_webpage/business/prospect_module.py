
from django.utils.translation import ugettext_lazy as _

import common

from dashboard.models import State
from beta_invite.models import EmailType
from testing_webpage.models import EmailSent
from business import search_module
from dashboard.models import Candidate
from beta_invite.util import email_sender
from testing_webpage import settings


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


def create_prospect_users_and_send_emails(campaign):
    """
    Args:
        campaign: obj
    Returns: Creates a list of prospect users on the DB. And sends all ot them an email.
    """

    email_type = EmailType.objects.get(name='job_match')

    # TODO: this feature only supports Spanish.
    search_text = search_module.with_lower_case_and_no_accents(campaign.title_es)
    users = search_module.get_matching_users(search_text=search_text,
                                             word_user_path='subscribe/word_user_dictionary.p')

    # Top 20 distinct users.
    users = get_distinct_users(users)
    users = filter_users_with_job(users)
    top_users = [u for u in users][:NUMBER_OF_MATCHES]

    for user in top_users:
        # check that emails are not sent twice and not to the same campaign where the user is already registered
        if not EmailSent.objects.filter(campaign=campaign, user=user, email_type=email_type) \
                and campaign not in common.get_campaigns(user):

            candidate = Candidate(campaign=campaign, user=user, state=State.objects.get(code='P'))
            candidate.save()

            if settings.DEBUG:
                candidate.user.email = 'juan@peaku.co'

            email_sender.send_to_candidate(candidates=candidate,
                                           language_code=user.language_code,
                                           body_input='user_job_match_email_body',
                                           subject=_('Open position for ') + campaign.title_es,
                                           override_dict={'campaign_url': campaign.get_url()})

            # Records sending email
            EmailSent(campaign=campaign, user=user, email_type=email_type).save()

