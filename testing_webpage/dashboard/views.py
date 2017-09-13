from django.shortcuts import render
from beta_invite.models import Campaign, User
from dashboard.models import State, Candidate
from dashboard import constants as cts


def index(request):
    """
    Args:
        request: HTTP
    Returns: renders main view with a list of campaigns
    """
    campaigns = Campaign.objects.all()
    return render(request, cts.MAIN_DASHBOARD, {'campaigns': campaigns})


def fill_in_missing_candidates(users, campaign_id):
    """
    Args:
        users: List of object User
        campaign_id: int id
    Returns: None, just fills into DB missing Candidates. Every new Candidate is created on the default state.
    """
    for u in users:
        if len(Candidate.objects.filter(campaign_id=campaign_id, user_id=u.id)) == 0:
            Candidate(campaign_id=campaign_id, user_id=u.id, state_id=cts.DEFAULT_STATE).save()


def campaign_edit(request, pk):
    """
    Args:
        request: HTTP
        pk: campaign primary key
    Returns: This controls the candidates dashboard
    """

    # enters here when saving changes
    if request.method == 'POST':

        candidates = Candidate.objects.filter(campaign_id=pk)

        for c in candidates:
            c.state_id = request.POST.get('{}_state'.format(c.id))
            c.comment = request.POST.get('{}_comment'.format(c.id))
            c.save()

    states = State.objects.all()

    # create missing candidates on the first try
    users = User.objects.filter(campaign_id=pk)

    fill_in_missing_candidates(users, pk)

    # TODO: recycle business search. Lot of work here: has to search according to campaign specification (education, profession, etc)
    candidates = Candidate.objects.filter(campaign_id=pk)

    return render(request, cts.DASHBOARD_EDIT, {'states': states,
                                                'campaign_id': pk,
                                                'candidates': candidates
                                                })
