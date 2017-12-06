"""
Updates the new users by initializing their candidate objects and updating their states.
"""

import os
from datetime import datetime, timedelta
from django.core.wsgi import get_wsgi_application

# Environment can use the models as if inside the Django app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

from beta_invite.models import User
from dashboard.models import Candidate
from dashboard import candidate_module


def create_and_update_candidates():
    """
    Fills into DB missing Candidates. Every new Candidate is created on the default state or in the
    WFI state.
    """

    # takes users created on the last day.
    users = User.objects.filter(created_at__range=(datetime.utcnow() - timedelta(days=1), datetime.utcnow()))

    for user in users:

        candidates = Candidate.objects.filter(campaign_id=user.campaign_id, user_id=user.id)

        # Create
        if len(candidates) == 0:
            candidate_module.fill_in_missing_candidate(user.campaign_id, user)
        else:  # Update
            candidate = candidates.first()
            candidate_module.update_candidate_state(candidate, user)


create_and_update_candidates()
