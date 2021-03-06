"""
This module returns score for a variety of searches. It is for development, benchmarking and improvement only
"""

import os
from django.core.wsgi import get_wsgi_application

# Environment can use the models as if inside the Django app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

import numpy as np
from copy import copy
from django.db.models import Q

from beta_invite.models import Campaign
from business import prospect_module
from dashboard.models import Candidate, State


# distribution by position of clicks on google search results:
# https://searchenginewatch.com/sew/study/2276184/no-1-position-in-google-gets-33-of-search-traffic-study
# The value is a percentage of clicks from the total and the position is the position on the search results.
SEARCH_BY_POSITION = [
    0.325,
    0.176,
    0.114,
    0.081,
    0.061,
    0.044,
    0.035,
    0.031,
    0.026,
    0.024
]


def get_search_target_for_candidate(candidate):
    """
    Contrast between very good and very bad candidates, where decisions have already been made explicitly
    No ambiguous states (such as Backlog, Did Interview etc.)
    :param candidate:
    :return: 1 = Very Good Match, 0 = Bad match, np.nan = unknown
    """
    if candidate.state in State.get_recommended_states() + State.get_relevant_states():
        return 1
    else:
        return 0


def get_score(candidates):
    """
    This is a weighted average, in order of relevance.
    :param candidates:
    :return: average score for a search list. Can return None if no candidates found upon search
    """
    # TODO: From previous function 'candidates_from_users' it is assumming that all candidates are found.
    # Which is far from true.

    # truncates to shorter list
    search_by_position = copy(SEARCH_BY_POSITION)
    min_length = min(len(search_by_position), len(candidates))
    candidates = candidates[:min_length]
    search_by_position = search_by_position[:min_length]

    # rescaling.
    search_by_position = [r/sum(search_by_position) for r in search_by_position]

    # get score per candidate
    my_list = [get_search_target_for_candidate(c) * r for r, c in zip(search_by_position, candidates)]

    if len(my_list) > 0:
        return np.nansum(np.array(my_list))
    else:
        return np.nan


def candidates_from_users(users, campaign):
    """
    Finds all candidates who are not in Prospect state, for a given campaign and in a list of possible users.
    Candidates are sorted from most likely to least likely.
    :param users: List of User obj
    :param campaign: Campaign obj
    :return: List of Candidate obj
    """
    candidates = []
    for user in users:

        try:
            candidate = Candidate.objects.get(~Q(state__code='P'), user=user, campaign=campaign)
            candidates.append(candidate)
        except:
            pass

    return candidates


def get_search_score():
    """simulates a  prospect search for each campaign then returns the average score"""
    scores = []
    campaigns = Campaign.objects.all()

    for campaign in campaigns:

        top_users = prospect_module.get_top_users_with_log(campaign)
        candidates = candidates_from_users(top_users, campaign)
        print(candidates)

        score = get_score(candidates)
        print('SEARCH SCORE campaign: {campaign}: score: {score}'.format(campaign=campaign,
                                                                         score=score))
        scores.append(score)

    if len(scores) > 0:
        return np.nanmean(scores)
    else:
        return np.nan


if __name__ == '__main__':
    print('FINAL SEARCH SCORE: ' + str(get_search_score()))
