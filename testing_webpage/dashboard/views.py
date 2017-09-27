from django.shortcuts import render
from beta_invite.models import Campaign, User, Evaluation
from dashboard.models import State, Candidate
from dashboard import constants as cts
from beta_invite.util import email_sender
from beta_invite.views import save_curriculum_from_request


def index(request):
    """
    Args:
        request: HTTP
    Returns: renders main view with a list of campaigns
    """
    campaigns = Campaign.objects.all()
    return render(request, cts.MAIN_DASHBOARD, {'campaigns': campaigns})


def has_passing_evaluation(evaluations):
    """
    Tries to find a passed evaluation.
    Args:
        evaluations: Collection of Evaluation objects.
    Returns: Boolean
    """
    for e in evaluations:
        if e.passed:
            return True

    return False


def update_candidate_state(candidate, user):
    """
    Changes state if test were presented or have improved.
    Args:
        candidate: Object
        user: Object
    Returns: None, just updates
    """

    if len(user.evaluations.all()) > 0:

        if has_passing_evaluation(user.evaluations.all()):
            candidate.state = State.objects.get(code='WFI')
            candidate.save()
        else:  # Fails tests
            candidate.state = State.objects.get(code='WFT')
            candidate.save()


def fill_in_missing_candidate(campaign_id, user):
    """
    Creates a new candidate, depending on several factors.
    Args:
        campaign_id: Campaign id, int
        user: Object
    Returns:
    """

    # Gets any evaluations, and if passed starts on the Waiting for Interview state.
    if len(user.evaluations.all()) > 0:
        if has_passing_evaluation(user.evaluations.all()):
            Candidate(campaign_id=campaign_id, user_id=user.id, state=State.objects.get(code='WFI')).save()
        else:
            # When fails, then we give the chance of presenting again.
            Candidate(campaign_id=campaign_id, user_id=user.id, state=State.objects.get(code='WFT')).save()
    else:
        # Starts on Backlog default state, when no evaluation has been done.
        Candidate(campaign_id=campaign_id, user_id=user.id).save()


def fill_and_update_candidates(users, campaign_id):
    """
    Args:
        users: List of object User
        campaign_id: int id
    Returns: None, just fills into DB missing Candidates. Every new Candidate is created on the default state or in the
    WFI state.
    """
    for user in users:

        candidates = Candidate.objects.filter(campaign_id=campaign_id, user_id=user.id)

        # Create
        if len(candidates) == 0:
            fill_in_missing_candidate(campaign_id, user)
        else:  # Update
            candidate = candidates.first()
            update_candidate_state(candidate, user)


def get_checked_box_users(campaign_id, request):
    candidates = Candidate.objects.filter(campaign_id=campaign_id)
    return [c.user for c in candidates if request.POST.get('{}_checkbox'.format(c.id))]


# TODO: make this available on different langs. Has a hardcoded title_es
def get_subject(request, campaign_id):
    campaign = Campaign.objects.get(pk=campaign_id)

    # passes on the '{name}', in case there is any.
    return request.POST.get('email_subject').format(campaign_name=campaign.title_es,
                                                    name='{name}')


def user_in_campaign(user_id, campaign_id):
    candidates = Candidate.objects.filter(user_id=user_id, campaign_id=campaign_id)
    return len(candidates) > 0


def add_candidate_to_campaign(request, candidate):
    """
    Adds candidate to another campaign.
    Args:
        request: A HTTP request
        candidate: Candidate object
    Returns: Error message if user already is in campaign
    """

    # Updates latest changes, first.
    update_candidate(request, candidate)

    selected_campaign_id = int(request.POST.get('{}_selected_campaign'.format(candidate.id)))

    if selected_campaign_id == cts.CAMPAIGN_ID_NULL or user_in_campaign(candidate.user_id, selected_campaign_id):
        return False
    else:
        Candidate(user_id=candidate.user_id,
                  campaign_id=selected_campaign_id,
                  state=candidate.state,
                  comment=candidate.comment).save()
        return True


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
    # create missing candidates on the first try, that have not been removed previously
    users = User.objects.filter(campaign_id=campaign_id)

    fill_and_update_candidates(users, campaign_id)

    # TODO: recycle business search. Lot of work here: has to search according to campaign specification (education, profession, etc)
    # Orders by desc priority field on the state object.
    backlog = get_candidates_from_state('BL', campaign_id)
    waiting_tests = get_candidates_from_state('WFT', campaign_id)
    waiting_interview = get_candidates_from_state('WFI', campaign_id)
    sent_to_client = get_candidates_from_state('STC', campaign_id)
    got_job = get_candidates_from_state('GTJ', campaign_id)

    rejected_candidates = Candidate.objects.filter(campaign_id=campaign_id,
                                                   state__is_rejected=True,
                                                   removed=False).order_by('-state__priority')

    return backlog, waiting_tests, waiting_interview, sent_to_client, got_job, rejected_candidates, State.objects.all()


def update_candidate(request, candidate):
    """
    Args:
        request: HTTP
        candidate: Object
    Returns: Saves Candidate and optionally the curriculum.
    """
    candidate.state_id = request.POST.get('{}_state'.format(candidate.id))
    candidate.comment = request.POST.get('{}_comment'.format(candidate.id))

    salary = request.POST.get('{}_salary'.format(candidate.id))
    if salary is not None:
        candidate.salary = salary

    candidate.save()

    filename = save_curriculum_from_request(request, candidate.user, '{}_curriculum'.format(candidate.id))

    if filename != '#':
        candidate.user.curriculum_url = filename
        candidate.user.save()


# TODO: use Ajax to optimize rendering. Has no graphics therefore is very low priority.
def campaign_edit(request, pk):
    """
    Args:
        request: HTTP
        pk: campaign primary key
    Returns: This controls the candidates dashboard
    """

    action = request.POST.get('action')
    candidate_id = request.POST.get('candidate_id')
    if candidate_id is not None:
        candidate = Candidate.objects.get(pk=int(candidate_id))

        if action == 'update':
            update_candidate(request, candidate)
        elif action == 'add':
            add_candidate_to_campaign(request, candidate)
        elif action == 'remove':
            remove_candidate(candidate)
        elif action == 'move':
            if add_candidate_to_campaign(request, candidate):  # only erase if has add successfully
                remove_candidate(candidate)

    # TODO: can be done with JS in smarter way???
    # enters here when sending an email
    if request.POST.get('send_mail') is not None:

        users = get_checked_box_users(pk, request)

        email_sender.send(users=users,
                          language_code=request.LANGUAGE_CODE,
                          body_input=request.POST.get('email_body'),
                          subject=get_subject(request, pk),
                          with_localization=False,
                          body_is_filename=False)

    backlog, waiting_tests, waiting_interview, sent_to_client, got_job, rejected, states = get_rendering_data(pk)

    # all campaigns except the current one.
    campaigns_to_move_to = Campaign.objects.exclude(pk=pk)

    return render(request, cts.DASHBOARD_EDIT, {'states': states,
                                                'campaign_id': pk,
                                                'backlog': backlog,
                                                'waiting_tests': waiting_tests,
                                                'waiting_interview': waiting_interview,
                                                'sent_to_client': sent_to_client,
                                                'got_job': got_job,
                                                'rejected': rejected,
                                                'campaigns': campaigns_to_move_to,
                                                'current_campaign': Campaign.objects.get(pk=pk)
                                                })
