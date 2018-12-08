"""
This task runs sync and sends emails from a table.
"""
import os
import sys
import platform
from django.core.wsgi import get_wsgi_application

# Environment can use the models as if inside the Django app
dir_separator = '\\' if 'Windows' == platform.system() else '/'
# how deep is this file from the project working directory?
dir_depth = len(''.join(os.getcwd().split('testing_webpage/', 1)[1]).split(dir_separator))
path_to_add = dir_separator.join(os.getcwd().split(dir_separator)[:-dir_depth])
sys.path.insert(0, path_to_add)

# Environment can use the models as if inside the Django app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

from testing_webpage.models import CandidatePendingEmail, CandidateEmailSent, BusinessUserEmailSent,\
    BusinessUserPendingEmail
from beta_invite.util import email_sender
from testing_webpage import settings
from dashboard.models import Candidate
from business.models import BusinessUser


# The maximum number of mails that sends at once.
MAX_NUMBER_OF_MAILS = 1  # TODO: change this later
TEST_EMAIL = 'juan@peaku.co'


def take_oldest_unsent_emails():
    return [e for e in BusinessUserPendingEmail.objects.filter(sent=False).order_by('created_at')] +\
           [e for e in CandidatePendingEmail.objects.filter(sent=False).order_by('created_at')]


def send_condition(an_object, email):
    return isinstance(an_object, Candidate) and \
           not CandidateEmailSent.objects.filter(candidate=an_object, email_type=email.email_type) or \
           isinstance(an_object, BusinessUser) and \
           not BusinessUserEmailSent.objects.filter(business_user=an_object, email_type=email.email_type)


def send_pending_emails():
    """
    Returns: Sends
    """

    pending = take_oldest_unsent_emails()[:MAX_NUMBER_OF_MAILS]

    for email in pending:
        if isinstance(email, CandidatePendingEmail):
            objects = email.candidates.all()
        else:
            objects = email.business_users.all()

        for an_object in objects:

            if send_condition(an_object, email):

                #if settings.DEBUG:  # TODO: add this now!!!
                if isinstance(an_object, Candidate):
                    an_object.user.email = TEST_EMAIL
                else:
                    an_object.email = TEST_EMAIL

                email_sender.send(objects=an_object,
                                  language_code=email.language_code,
                                  body_input=email.body_input,
                                  subject=email.subject,
                                  override_dict=email.override_dict)

                email.sent = True
                email.save()
                print('sent email "{}" to {}'.format(email.subject, an_object.email))

                # Records sending email
                if isinstance(an_object, Candidate):
                    CandidateEmailSent(candidate=an_object, email_type=email.email_type).save()
                else:
                    BusinessUserEmailSent(business_user=an_object, email_type=email.email_type).save()


if __name__ == '__main__':
    print('sending emails...')
    send_pending_emails()
    print('finished sending emails...')
