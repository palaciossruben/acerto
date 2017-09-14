from django.shortcuts import render
from beta_invite.models import Campaign, User
from dashboard.models import State, Candidate
from dashboard import constants as cts
from beta_invite.util import email_sender


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


def get_checked_box_users(campaign_id, request):
    candidates = Candidate.objects.filter(campaign_id=campaign_id)
    return [c.user for c in candidates if request.POST.get('{}_checkbox'.format(c.id))]


# TODO: make this available on different langs.
def get_subject(request, campaign_id):
    campaign = Campaign.objects.filter(pk=campaign_id).first()
    return request.POST.get('email_subject').format(campaign_name=campaign.title_es)


# TODO: use Ajax to optimize rendering. Has no graphics therefore is very low priority.
def campaign_edit(request, pk):
    """
    Args:
        request: HTTP
        pk: campaign primary key
    Returns: This controls the candidates dashboard
    """

    # enters here when saving changes
    if request.POST.get('save_changes') is not None:

        candidates = Candidate.objects.filter(campaign_id=pk)

        for c in candidates:
            c.state_id = request.POST.get('{}_state'.format(c.id))
            c.comment = request.POST.get('{}_comment'.format(c.id))
            c.save()

    # enters here when sending an email
    if request.POST.get('send_mail') is not None:

        users = get_checked_box_users(pk, request)

        email_sender.send(users=users,
                          language_code=request.LANGUAGE_CODE,
                          body_input=request.POST.get('email_body'),
                          subject=get_subject(request, pk),
                          with_localization=False,
                          body_is_filename=False)

    # enters here when adding a candidate to another campaign.
    # TODO: make thins great again.

    states = State.objects.all()

    # create missing candidates on the first try
    users = User.objects.filter(campaign_id=pk)

    fill_in_missing_candidates(users, pk)

    # TODO: recycle business search. Lot of work here: has to search according to campaign specification (education, profession, etc)
    # Orders by desc priority field on the state object.
    candidates = Candidate.objects.filter(campaign_id=pk).order_by('-state__priority')

    return render(request, cts.DASHBOARD_EDIT, {'states': states,
                                                'campaign_id': pk,
                                                'candidates': candidates
                                                })
