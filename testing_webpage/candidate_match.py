"""
Sends emails to users reminding them of common tasks: do the tests or do the interview, etc
"""

import os
from django.core.wsgi import get_wsgi_application

# Environment can use the models as if inside the Django app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

import time
import pickle
from datetime import datetime
from dashboard.models import Candidate
from business import search_module


def process_all_candidates_match():
    """
    Gets all matching scores.
    :return: adds matching scores to all candidates
    """
    candidates = Candidate.objects.filter(match=None)
    campaigns = {c.campaign for c in candidates}

    for campaign in campaigns:

        campaign_text = campaign.get_search_text()
        word_array = search_module.get_word_array_lower_case_and_no_accents(campaign_text)

        campaign_users = {c.user for c in candidates if c.campaign.pk == campaign.pk}

        word_user_dictionary = pickle.load(open(search_module.WORD_USER_PATH, 'rb'))

        sorted_iterator = search_module.user_id_sorted_iterator(word_user_dictionary, campaign_users, word_array)

        # TODO: Missing relevance normalization
        for user_id, relevance in sorted_iterator:

            # Pick any candidate.
            candidate = [c for c in candidates if c.user and c.user.id == user_id][0]
            candidate.text_match = relevance
            candidate.save()


if __name__ == '__main__':
    t0 = time.time()
    process_all_candidates_match()
    t1 = time.time()
    print('On {0} CANDIDATE_MATCH, took: {1}'.format(datetime.today(), t1 - t0))
