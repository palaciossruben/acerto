"""
All functions related to candidates, dashboard stuff.
"""

from dashboard.models import Comment, Candidate, State
from beta_invite.models import Campaign
from dashboard import constants as cts
from beta_invite import new_user_module


def add_property(candidate, request, property_name):
    property = request.POST.get('{0}_{1}'.format(candidate.id, property_name))
    if property is not None and property != '':
        setattr(candidate, property_name, property)


def update_candidate(request, candidate):
    """
    Args:
        request: HTTP
        candidate: Object
    Returns: Saves Candidate and optionally the curriculum.
    """
    candidate.state_id = request.POST.get('{}_state'.format(candidate.id))

    text = request.POST.get('{}_comment'.format(candidate.id))
    if text is not None and text != '':

        comment = Comment(text=text)
        comment.save()
        candidate.comments.add(comment)

    add_property(candidate, request, 'salary')
    add_property(candidate, request, 'screening_id')
    add_property(candidate, request, 'screening_explanation')

    candidate.save()

    new_user_module.update_resource(request, candidate.user, 'curriculum_url', 'resumes')


def add_candidate_to_campaign(request, candidate):
    """
    Adds candidate to another campaign.
    Args:
        request: A HTTP request
        candidate: Candidate object
    Returns: Boolean indicating whether a new candidate was added
    """

    # Updates latest changes, first.
    update_candidate(request, candidate)

    selected_campaign_id = int(request.POST.get('{}_selected_campaign'.format(candidate.id)))

    if selected_campaign_id == cts.CAMPAIGN_ID_NULL or user_in_campaign(candidate.user_id, selected_campaign_id):
        return False
    else:
        # Starts in Backlog on the new campaign.
        # TODO: can add logic to new at a later stage, if tests are already passed.
        Candidate(user_id=candidate.user_id,
                  campaign_id=selected_campaign_id,
                  state=State.objects.get(code='BL')).save()

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
    return Candidate.objects.filter(campaign_id=campaign_id,
                                    state__is_rejected=False,
                                    state=State.objects.get(code=state_code),
                                    removed=False)


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

    candidates_dict['rejected'] = Candidate.objects.filter(campaign_id=campaign_id,
                                                           state__is_rejected=True,
                                                           removed=False)

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
