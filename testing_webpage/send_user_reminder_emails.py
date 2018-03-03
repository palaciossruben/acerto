"""
Sends emails to users reminding them of common tasks: do the tests or do the interview, etc
"""

import os
from datetime import datetime, timedelta
from django.core.wsgi import get_wsgi_application

# Environment can use the models as if inside the Django app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

from beta_invite import interview_module
from beta_invite.util import email_sender
from dashboard.models import Candidate
from beta_invite.models import Campaign, EmailType
from testing_webpage.models import EmailSent
from business import prospect_module


def get_recently_created_new_state_candidates(state):
    """
    Returns: Gets candidates which are on a new state, created in between 1 and 25 hours ago.
    """
    # TODO: missing boolean indicating whether the email was sent.
    start_date = datetime.utcnow() - timedelta(hours=25)
    end_date = datetime.utcnow() - timedelta(hours=1)
    return Candidate.objects.filter(state__name=state, created_at__range=(start_date, end_date))


def translate_email_test_subject(candidate):
    """
    Default will be in spanish
    Args:
        candidate: Candidate object
    Returns: translated subject
    """
    if candidate.user.language_code is None or candidate.user.language_code == 'es':
        return 'Te invito a hacer la prueba para {campaign}'.format(campaign=candidate.campaign.title_es)
    else:
        return 'I invite you to do the test for {campaign}'.format(campaign=candidate.campaign.title)


def translate_email_interview_subject(candidate):
    """
    Default will be in spanish
    Args:
        candidate: User object
    Returns: translated subject
    """
    if candidate.user.language_code is None or candidate.user.language_code == 'es':
        return 'Puedes grabar la entrevista para {campaign}'.format(campaign=candidate.campaign.title_es)
    else:
        return 'You can record the interview for {campaign}'.format(campaign=candidate.campaign.title)


def send_reminder(email_template, state_name, subject_function, email_type):
    """
    Sends a reminder to all users who have registered in between 25 to 1 hour ago
    Returns: send email like crazy
    """

    candidates = get_recently_created_new_state_candidates(state_name)

    for candidate in candidates:
        if candidate.campaign.pk != 5:
            #  Do not send if there are no tests or is on the 'WFI' and has no interviews.
            if not candidate.campaign.tests or state_name == 'Waiting For Interview' \
                    and not interview_module.has_recorded_interview(candidate.campaign):
                continue

            # check that emails are not sent twice with respect to a candidate:
            if not EmailSent.objects.filter(campaign=candidate.campaign, candidate=candidate, email_type=email_type):

                email_sender.send_to_candidate(candidates=candidate,
                                               language_code=candidate.user.language_code,
                                               body_input=email_template,
                                               subject=subject_function(candidate))

                # Records sending email
                EmailSent(campaign=candidate.campaign, candidate=candidate, email_type=email_type).save()

    return


def send_possible_job_matches():
    """
    Returns: Sends emails with all possible job matches (People who's CV match closely with a given campaign).
    """

    # Active campaigns that are not the default campaign
    active_campaigns = Campaign.objects.filter(active=True)

    for campaign in active_campaigns:
        prospect_module.create_prospect_users_and_send_emails(campaign)


if __name__ == '__main__':
    send_reminder(email_template='user_test_reminder_email_body',
                  state_name='Backlog',
                  subject_function=translate_email_test_subject,
                  email_type=EmailType.objects.get(name='backlog', sync=True))
    '''
    send_reminder(email_template='user_interview_reminder_email_body',
                  state_name='Waiting for Interview',
                  subject_function=translate_email_interview_subject,
                  email_type=EmailType.objects.get(name='interview', sync=True))
    '''
    send_possible_job_matches()
