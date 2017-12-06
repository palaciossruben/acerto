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


def get_recently_created_backlog_candidates():
    """
    Returns: Gets candidates which are on backlog, created in between 1 and 25 hours ago.
    """
    # TODO: missing boolean indicating whether the email was sent.
    start_date = datetime.utcnow() - timedelta(hours=25)
    end_date = datetime.utcnow() - timedelta(hours=1)
    return Candidate.objects.filter(state__name="Backlog", created_at__range=(start_date, end_date))


def translate_email_subject(user):
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


def send_test_reminder():
    """
    Sends a reminder to all users who have registered in between 25 to 1 hour ago, asking to complete the tests.
    Returns: send email like crazy
    """

    candidates = get_recently_created_backlog_candidates()

    for candidate in candidates:
        user = candidate.user
        email_sender.send(users=user,
                          language_code=user.language_code,
                          body_input='user_test_reminder_email_body',
                          subject=translate_email_subject(user))


send_test_reminder()
