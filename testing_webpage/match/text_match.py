"""
Calculates the text_match between campaign and CV to estimate compatibility.
"""

import os
import pickle
from dashboard.models import Candidate
from business import search_module


def update(force_update=False):
    """
    Gets all matching scores.
    :return: adds matching scores to all candidates
    """

    if force_update:
        candidates = Candidate.objects.all()
    else:
        candidates = Candidate.objects.filter(text_match=None)

    campaigns = {c.campaign for c in candidates}

    for campaign in campaigns:

        campaign_text = campaign.get_search_text()
        word_array = search_module.get_word_array_lower_case_and_no_accents(campaign_text)

        campaign_users = {c.user for c in candidates if c.campaign.pk == campaign.pk}

        word_user_dictionary = pickle.load(open(search_module.WORD_USER_PATH, 'rb'))

        sorted_iterator = search_module.user_id_sorted_iterator(word_user_dictionary, campaign_users, word_array)

        # TODO: Missing relevance normalization
        for user_id, relevance in sorted_iterator:

            for c in candidates:
                if c.user and c.user.id == user_id:
                    c.text_match = relevance
                    c.save()
