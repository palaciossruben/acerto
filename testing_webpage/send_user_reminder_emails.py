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
from beta_invite.models import Campaign, EmailType, EmailSent

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


def translate_email_job_match_subject(user, campaign):
    """
    Default will be in spanish
    Args:
        user: User object
    Returns: translated subject
    """
    if user.language_code is None or user.language_code == 'es':
        return 'Vacantes abierta para {campaign}'.format(campaign=campaign.title_es)
    else:
        return 'Open position for {campaign}'.format(campaign=user.campaign.title)


def send_reminder(email_template, state_name, subject_function, email_type):
    """
    Sends a reminder to all users who have registered in between 25 to 1 hour ago
    Returns: send email like crazy
    """

    candidates = get_recently_created_new_state_candidates(state_name)

    for candidate in candidates:
        user = candidate.user

        # do not send if there are no tests.
        if not user.campaign.tests or state_name == 'Waiting For Interview' and not user.campaign.interviews:
            continue

        # check that emails are not sent twice:
        if not EmailSent.objects.filter(campaign=user.campaign, user=user, email_type=email_type):
            email_sender.send(users=user,
                              language_code=user.language_code,
                              body_input=email_template,
                              subject=subject_function(user))

            # Records sending email
            EmailSent(campaign=user.campaign, user=user, email_type=email_type).save()
            return

    return


def get_distinct_users(users):
    """
    Args:
        users: Users QuerySet.
    Returns: Only sends email ones, to a given email.
    """
    return users.order_by().distinct('email')


def send_possible_job_matches():
    """
    Returns: Sends emails with all possible job matches (People who's CV match closely with a given campaign).
    """
    email_type = EmailType.objects.get(name='job_match', sync=True)

    active_campaigns = Campaign.objects.filter(active=True)

    for campaign in active_campaigns:

        # TODO: this feature only supports Spanish.
        search_text = search_module.with_lower_case_and_no_accents(campaign.title_es)
        users = search_module.get_matching_users2(search_text=search_text,
                                                  word_user_path='subscribe/word_user_dictionary.p')

        for user in get_distinct_users(users):

            # check that emails are not sent twice and not to the same campaign where the user is already registered
            if not EmailSent.objects.filter(campaign=campaign, email_type=email_type, user__email=user.email)\
                    and user.campaign != campaign:

                email_sender.send(users=user,
                                  language_code=user.language_code,
                                  body_input='user_job_match_email_body',
                                  subject=translate_email_job_match_subject(user, campaign),
                                  override_dict={'campaign_url': campaign.get_url()})

                # Records sending email
                EmailSent(campaign=campaign, user=user, email_type=email_type).save()


send_reminder(email_template='user_test_reminder_email_body',
              state_name='Backlog',
              subject_function=translate_email_test_subject,
              email_type=EmailType.objects.get(name='job_match', sync=True))
send_reminder(email_template='user_interview_reminder_email_body',
              state_name='Waiting for Interview',
              subject_function=translate_email_interview_subject,
              email_type=EmailType.objects.get(name='interview', sync=True))
send_possible_job_matches()
