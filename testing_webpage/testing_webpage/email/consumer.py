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

import common
from testing_webpage.models import CandidatePendingEmail, CandidateEmailSent, BusinessUserEmailSent,\
    BusinessUserPendingEmail, CampaignPendingEmail, CampaignEmailSent
from beta_invite.util import email_sender
from testing_webpage import settings
from dashboard.models import Candidate, Campaign
from business.models import BusinessUser
from subscribe import helper as h
from decouple import config
from raven import Client

# The maximum number of mails that sends at once.
MAX_NUMBER_OF_MAILS = 10
TEST_EMAIL = 'juan@peaku.co'
SENTRY_CLIENT = Client(config('sentry_dsn'))


def take_oldest_unsent_emails():
    return list(BusinessUserPendingEmail.objects.filter(sent=False, processed=False).order_by('created_at')[:MAX_NUMBER_OF_MAILS]) + \
           list(CandidatePendingEmail.objects.filter(sent=False, processed=False).order_by('created_at')[:MAX_NUMBER_OF_MAILS]) + \
           list(CampaignPendingEmail.objects.filter(sent=False, processed=False).order_by('created_at')[:MAX_NUMBER_OF_MAILS])


def send_condition_with_class(an_object, object_class, email, email_class):

    num_emails = len(email_class.objects.filter(an_object=an_object, email_type=email.email_type))

    return isinstance(an_object, object_class) and \
        (email.email_type.send_more_than_ones or not num_emails)


def send_condition(an_object, email):
    """
    Sends if the EmailType should be sent many times or if hasn't been sent at least one time.
    :param an_object: Candidate, BusinessUser, Campaign
    :param email: obj
    :return: Boolean
    """

    # TODO: missing a refactor
    """return send_condition_with_class(an_object, Candidate, email, CandidatePendingEmail) or \
           send_condition_with_class(an_object, BusinessUser, email, BusinessUserPendingEmail) or \
           send_condition_with_class(an_object, Campaign, email, CampaignPendingEmail)"""

    return isinstance(an_object, Candidate) and \
        (email.email_type.send_more_than_ones or not CandidateEmailSent.objects.filter(an_object=an_object, email_type=email.email_type)) or \
        isinstance(an_object, BusinessUser) and \
        (email.email_type.send_more_than_ones or not BusinessUserEmailSent.objects.filter(an_object=an_object, email_type=email.email_type)) or \
        isinstance(an_object, Campaign) and \
        (email.email_type.send_more_than_ones or not CampaignEmailSent.objects.filter(an_object=an_object, email_type=email.email_type))


def get_email(an_object):
    if isinstance(an_object, Candidate):
        return an_object.user.email
    elif isinstance(an_object, BusinessUser):
        return an_object.email
    elif isinstance(an_object, Campaign):
        business_user = common.get_business_user_with_campaign(an_object)
        return business_user.email
    else:
        raise NotImplementedError('Unimplemented class: {}'.format(type(an_object)))


def send_one_email(email):
    """
    This email can have several recipients...
    :param email:
    :return:
    """
    for an_object in email.the_objects.all():

        if send_condition(an_object, email):

            if settings.DEBUG:
                if isinstance(an_object, Candidate):
                    an_object.user.email = TEST_EMAIL
                elif isinstance(an_object, BusinessUser):
                    an_object.email = TEST_EMAIL
                elif isinstance(an_object, Campaign):
                    business_user = common.get_business_user_with_campaign(an_object)
                    business_user.email = TEST_EMAIL
                    business_user.save()  # heavy machete: no alternative here
                else:
                    raise NotImplementedError('Unimplemented class: {}'.format(type(an_object)))

            email_sender.send(objects=an_object,
                              language_code=email.language_code,
                              body_input=email.body_input,
                              subject=email.subject,
                              override_dict=email.override_dict)

            email.sent = True
            email.save()
            print('sent email "{}" to {}'.format(email.subject, get_email(an_object)))

            # Records sending email
            if isinstance(an_object, Candidate):
                CandidateEmailSent(an_object=an_object, email_type=email.email_type).save()
            elif isinstance(an_object, BusinessUser):
                BusinessUserEmailSent(an_object=an_object, email_type=email.email_type).save()
            elif isinstance(an_object, Campaign):
                CampaignEmailSent(an_object=an_object, email_type=email.email_type).save()
            else:
                raise NotImplementedError('Unimplemented class: {}'.format(type(an_object)))

    email.processed = True
    email.save()


def send_pending_emails():
    """
    Returns: Sends
    """

    pending = take_oldest_unsent_emails()

    for email in pending:
        try:
            send_one_email(email)
        except Exception as e:
            SENTRY_CLIENT.captureException()
            print('email: {} of type: {}, exception:'.format(email, type(email)))
            print(e)


if __name__ == '__main__':

    try:
        if settings.DEBUG:
            send_pending_emails()
        else:
            with open('consumer.log', 'a') as f:
                sys.stdout = h.Unbuffered(f)
                send_pending_emails()
    except Exception as e:
        SENTRY_CLIENT.captureException()
        print(e)
