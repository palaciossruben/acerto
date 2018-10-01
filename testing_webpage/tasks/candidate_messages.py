"""
This file adds key message on the Candidate Flux, that are not triggered by an endpoint
"""
import os
import sys

from django.core.wsgi import get_wsgi_application

# Environment can use the models as if inside the Django app
sys.path.insert(0, '/'.join(os.getcwd().split('/')[:-1]))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

import datetime
from django.db.models import Q

from dashboard.models import Candidate
from beta_invite.util import messenger_sender


def run():

    # TODO: THIS IS INACTIVE, needs the cron job:
    # 0 * * * * cd / home / ubuntu / acerto / testing_webpage / tasks & & python3 candidate_messages.py

    message_filename = 'candidate_backlog'

    # TODO: add English
    # Make sure that messages are not repeating
    candidates = [c for c in Candidate.objects.filter(Q(created_at__lt=datetime.datetime.today() - datetime.timedelta(hours=1)) &
                                                      Q(created_at__gt=datetime.datetime.today() - datetime.timedelta(hours=2)) &
                                                      Q(state__code='BL') &
                                                      ~Q(message__filename=message_filename))]

    messenger_sender.send(candidates=candidates,
                          language_code='es',
                          body_input=message_filename)


if __name__ == '__main__':
    run()
