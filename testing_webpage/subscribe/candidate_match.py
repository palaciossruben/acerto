"""
Sends emails to users reminding them of common tasks: do the tests or do the interview, etc
"""

import os
import time
from datetime import datetime, timedelta
from django.core.wsgi import get_wsgi_application

# Environment can use the models as if inside the Django app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

from dashboard.models import Candidate


def get_recently_created_new_state_candidates(state):
    """
    Returns: Gets candidates which are on a new state, created in between 1 and 25 hours ago.
    """
    # TODO: missing boolean indicating whether the email was sent.
    start_date = datetime.utcnow() - timedelta(hours=25)
    end_date = datetime.utcnow() - timedelta(hours=1)
    return Candidate.objects.filter(state__name=state, created_at__range=(start_date, end_date))


def get_all_candidates_match():

    candidates =


if __name__ == '__main__':
    t0 = time.time()
    get_all_candidates_match()
    t1 = time.time()
    print('On {0} CANDIDATE_MATCH, took: {1}'.format(datetime.today(), t1 - t0))

