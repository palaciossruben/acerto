"""
This task runs sync and sends emails from a table.
"""
import os
from django.core.wsgi import get_wsgi_application

# Environment can use the models as if inside the Django app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

from testing_webpage.models import PendingEmail, EmailSent
from beta_invite.util import email_sender
from testing_webpage import settings


# The maximum number of mails that sends at once.
MAX_NUMBER_OF_MAILS = 20


def take_oldest_unsent_emails():
    return PendingEmail.objects.filter(sent=False).order_by('created_at')[:MAX_NUMBER_OF_MAILS]


def send_pending_emails():
    """
    Returns: Sends
    """

    pending = take_oldest_unsent_emails()

    for email in pending:

        for candidate in email.candidates.all():

            if not EmailSent.objects.filter(candidate=candidate, email_type=email.email_type):

                if settings.DEBUG:
                    candidate.user.email = 'juan@peaku.co'

                email_sender.send(objects=candidate,
                                  language_code=email.language_code,
                                  body_input=email.body_input,
                                  subject=email.subject,
                                  override_dict=email.override_dict)

                email.sent = True
                email.save()

                # Records sending email
                EmailSent(candidate=candidate, email_type=email.email_type).save()


if __name__ == '__main__':
    send_pending_emails()
