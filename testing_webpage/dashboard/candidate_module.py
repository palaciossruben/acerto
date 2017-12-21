"""
All functions related to candidates, dashboard stuff.
"""

from beta_invite.views import save_curriculum_from_request
from dashboard.models import Comment, Candidate, State
from beta_invite.models import Campaign, User
from dashboard import constants as cts


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

    salary = request.POST.get('{}_salary'.format(candidate.id))
    if salary is not None and salary != '':
        candidate.salary = salary

    candidate.save()

    filename = save_curriculum_from_request(request, candidate.user, '{}_curriculum'.format(candidate.id))

    if filename != '#':
        candidate.user.curriculum_url = filename
        candidate.user.save()


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
        # TODO: can add logic to start at a later stage, if tests are already passed.
        new_candidate = Candidate(user_id=candidate.user_id,
                                  campaign_id=selected_campaign_id,
                                  state=State.objects.get(code='BL'))
        user = new_candidate.user
        user.campaign_id = selected_campaign_id
        user.save()
        new_candidate.save()
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
                                    removed=False).order_by('-state__priority')


def get_rendering_data(campaign_id):
    """
    Args:
        campaign_id: Campaign primary key
    Returns: tuple with (candidates, rejected_candidates, states)
    """

    # TODO: recycle business search. Lot of work here: has to search according to campaign specification
    # (education, profession, etc)
    # Orders by desc priority field on the state object.
    backlog = get_candidates_from_state('BL', campaign_id)
    waiting_tests = get_candidates_from_state('WFT', campaign_id)
    waiting_interview = get_candidates_from_state('WFI', campaign_id)
    did_interview_in_standby = get_candidates_from_state('DIS', campaign_id)
    sent_to_client = get_candidates_from_state('STC', campaign_id)
    got_job = get_candidates_from_state('GTJ', campaign_id)

    rejected_candidates = Candidate.objects.filter(campaign_id=campaign_id,
                                                   state__is_rejected=True,
                                                   removed=False).order_by('-state__priority')

    return backlog, waiting_tests, waiting_interview, did_interview_in_standby, sent_to_client, got_job, rejected_candidates, State.objects.all()


def get_checked_box_users(campaign_id, request):
    candidates = Candidate.objects.filter(campaign_id=campaign_id)
    return [c.user for c in candidates if request.POST.get('{}_checkbox'.format(c.id))]


# TODO: make this available on different langs. Has a hardcoded title_es
def get_subject(request, campaign_id):
    campaign = Campaign.objects.get(pk=campaign_id)

    # passes on the '{name}', in case there is any.
    return request.POST.get('email_subject').format(campaign_name=campaign.title_es,
                                                    name='{name}')
