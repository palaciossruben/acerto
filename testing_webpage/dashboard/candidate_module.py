"""
All functions related to candidates, dashboard stuff.
"""

from dashboard.models import Comment, Candidate, State
from beta_invite.models import Campaign, EvaluationSummary
from dashboard import constants as cts
from beta_invite import new_user_module
from beta_invite.models import Test, Score
from beta_invite import test_module


def add_property(candidate, request, property_name):
    my_property = request.POST.get('{0}_{1}'.format(candidate.id, property_name))
    if my_property is not None and my_property != '':
        setattr(candidate, property_name, my_property)


def update_test_value(evaluation, scores, value, test):

    if value is None or value == "":
        return

    value = float(value)
    update_flag = False
    for score in scores:
        if test == score.test:
            update_flag = True
            score.update(value=value)
            score.save()

    if not update_flag:
        score = Score(test=test, value=value)
        score.save()
        evaluation.scores.add(score)

    evaluation.save()


def updates_or_creates_score(evaluation, cultural_value, motivation_value):
    """
    **** Updates both Scores and Candidate objects. ****
    :param evaluation: obj
    :param cultural_value: float 0-100
    :param motivation_value: float 0-100
    :return: none
    """
    dummy_motivation_test = Test.objects.get(name='Motivation')
    dummy_cultural_test = Test.objects.get(name='Cultural fit')
    scores = evaluation.scores.all()

    update_test_value(evaluation, scores, motivation_value, dummy_motivation_test)
    update_test_value(evaluation, scores, cultural_value, dummy_cultural_test)


def update_candidate_with_tests(candidate, motivation_value, cultural_value):
    """
    Updates latest evaluation with scores of cultural fit and motivation
    :param candidate:
    :param motivation_value:
    :param cultural_value:
    :return:
    """
    candidate_evaluations = candidate.evaluations.all()

    if len(candidate_evaluations) > 0 and (motivation_value or cultural_value):

        if motivation_value:
            motivation_value = float(motivation_value)

        if cultural_value:
            cultural_value = float(cultural_value)

        evaluation = candidate.get_last_evaluation()

        # only updates if there is a change.
        if evaluation.motivation_score != motivation_value or evaluation.cultural_fit_score != cultural_value:

            updates_or_creates_score(evaluation,
                                     motivation_value=motivation_value,
                                     cultural_value=cultural_value)
            test_module.update_scores(evaluation, evaluation.scores.all())

            if candidate.evaluation_summary:
                candidate.evaluation_summary.update_evaluations(candidate.evaluations.all())
            else:
                candidate.evaluation_summary = EvaluationSummary.create(candidate.evaluations.all())

            test_module.classify_evaluation_and_change_state(candidate)


def update_candidate_manually(request, candidate):
    """
    Args:
        request: HTTP
        candidate: Object
    Returns: Saves Candidate and optionally the curriculum.
    """
    state_id = request.POST.get('{}_state'.format(candidate.id))
    candidate.change_state(state_code=State.objects.get(pk=state_id).code,
                           auth_user=request.user)

    text = request.POST.get('{}_comment'.format(candidate.id))
    if text is not None and text != '':

        comment = Comment(text=text)
        comment.save()
        candidate.comments.add(comment)

    add_property(candidate, request, 'salary')
    add_property(candidate, request, 'screening_id')
    add_property(candidate, request, 'screening_explanation')

    motivation_value = request.POST.get('{0}_{1}'.format(candidate.id, 'motivation'))
    cultural_value = request.POST.get('{0}_{1}'.format(candidate.id, 'cultural_fit'))
    update_candidate_with_tests(candidate, motivation_value, cultural_value)

    candidate.save()

    new_user_module.update_resource(request, candidate.user, 'curriculum_url', 'resumes')
    new_user_module.update_resource(request, candidate.user, 'photo_url', 'candidate_photo')


def add_candidate_to_campaign(request, candidate):
    """
    Adds candidate to another campaign.
    Args:
        request: A HTTP request
        candidate: Candidate object
    Returns: Boolean indicating whether a new candidate was added
    """

    # Updates latest changes, first.
    update_candidate_manually(request, candidate)

    selected_campaign_id = int(request.POST.get('{}_selected_campaign'.format(candidate.id)))

    if selected_campaign_id == cts.CAMPAIGN_ID_NULL or user_in_campaign(candidate.user_id, selected_campaign_id):
        return False
    else:
        # Starts in Backlog on the new campaign.
        # TODO: can add logic to new at a later stage, if tests are already passed.
        Candidate(user_id=candidate.user_id,
                  campaign_id=selected_campaign_id,
                  state=State.objects.get(code='P')).save()

        return True


def user_in_campaign(user_id, campaign_id):
    candidates = Candidate.objects.filter(user_id=user_id, campaign_id=campaign_id)
    return len(candidates) > 0


def remove_candidate(candidate):
    """
    Removes candidate.
    Args:
        candidate: Candidate object
    Returns: Error message user was already removed.
    """

    if user_in_campaign(candidate.user_id, candidate.campaign.id):
        candidate.removed = True
        candidate.save()
        return True
    else:
        return False


def get_candidates_from_state(state_code, campaign_id):
    candidates = Candidate.objects.filter(campaign_id=campaign_id,
                                          state__is_rejected=False,
                                          state=State.objects.get(code=state_code),
                                          removed=False)

    return [c for c in reversed(sorted(candidates,
                                       key=lambda c: c.get_average_final_score()))]


def get_rendering_data(campaign_id):
    """
    Args:
        campaign_id: Campaign primary key
    Returns: tuple with (candidates, rejected_candidates, states)
    """

    states = State.objects.filter(is_rejected=False)

    candidates_dict = {}
    for state in states:
        candidates_dict[state.name.lower().replace(' ', '_')] = get_candidates_from_state(state.code, campaign_id)

    rejected_candidates = Candidate.objects.filter(campaign_id=campaign_id,
                                                   state__is_rejected=True,
                                                   removed=False)

    candidates_dict['rejected'] = [c for c in reversed(sorted(rejected_candidates,
                                                              key=lambda c: c.get_average_final_score()))]

    return candidates_dict, State.objects.all()


def get_checked_box_candidates(campaign_id, request):
    candidates = Candidate.objects.filter(campaign_id=campaign_id)
    return [c for c in candidates if request.POST.get('{}_checkbox'.format(c.id))]


# TODO: make this available on different langs. Has a hardcoded title_es
def get_subject(request, campaign_id):
    campaign = Campaign.objects.get(pk=campaign_id)

    # passes on the '{name}', in case there is any.
    return request.POST.get('email_subject').format(campaign_name=campaign.title_es,
                                                    name='{name}')
