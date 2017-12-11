"""
Sends emails to users reminding them of common tasks: do the tests or do the interview, etc
"""

import os
from datetime import datetime, timedelta
from django.core.wsgi import get_wsgi_application

# Environment can use the models as if inside the Django app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

from beta_invite.util import email_sender
from dashboard.models import Candidate
from business import search_module
from beta_invite.models import Campaign

NUMBER_OF_MATCHES = 20


def get_recently_created_new_state_candidates(state):
    """
    Returns: Gets candidates which are on a new state, created in between 1 and 25 hours ago.
    """
    # TODO: missing boolean indicating whether the email was sent.
    start_date = datetime.utcnow() - timedelta(hours=25)
    end_date = datetime.utcnow() - timedelta(hours=1)
    return Candidate.objects.filter(state__name=state, created_at__range=(start_date, end_date))


def translate_email_test_subject(user):
    """
    Default will be in spanish
    Args:
        user: User object
    Returns: translated subject
    """
    if user.language_code is None or user.language_code == 'es':
        return 'Te invito a hacer la prueba para {campaign}'.format(campaign=user.campaign.title_es)
    else:
        return 'I invite you to do the test for {campaign}'.format(campaign=user.campaign.title)


def translate_email_interview_subject(user):
    """
    Default will be in spanish
    Args:
        user: User object
    Returns: translated subject
    """
    if user.language_code is None or user.language_code == 'es':
        return 'Puedes grabar la entrevista para {campaign}'.format(campaign=user.campaign.title_es)
    else:
        return 'You can record the interview for {campaign}'.format(campaign=user.campaign.title)


def translate_email_job_match_subject(user):
    """
    Default will be in spanish
    Args:
        user: User object
    Returns: translated subject
    """
    if user.language_code is None or user.language_code == 'es':
        return 'Vacantes abierta para {campaign}'.format(campaign=user.campaign.title_es)
    else:
        return 'Open position for {campaign}'.format(campaign=user.campaign.title)


def send_reminder(email_template, state, subject_function):
    """
    Sends a reminder to all users who have registered in between 25 to 1 hour ago
    Returns: send email like crazy
    """

    candidates = get_recently_created_new_state_candidates(state)

    for candidate in candidates:
        user = candidate.user
        email_sender.send(users=user,
                          language_code=user.language_code,
                          body_input=email_template,
                          subject=subject_function(user))


def send_possible_job_matches():
    """
    Returns: Sends emails with all possible job matches (People who's CV match closely with a given campaign).
    """
    active_campaigns = Campaign.objects.filter(active=True)

    for campaign in active_campaigns:

        # TODO: this feature only supports Spanish.
        search_text = search_module.with_lower_case_and_no_accents(campaign.title_es)
        users = search_module.get_matching_users2(search_text=search_text,
                                                  word_user_path='subscribe/word_user_dictionary.p')

        for user in users:
            email_sender.send(users=user,
                              language_code=user.language_code,
                              body_input='user_job_match_email_body',
                              subject=translate_email_job_match_subject(user))


#send_reminder('user_test_reminder_email_body', 'Backlog', translate_email_test_subject)
#send_reminder('user_interview_reminder_email_body', 'Waiting for Interview', translate_email_interview_subject)
#send_possible_job_matches()
