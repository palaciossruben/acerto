from dashboard import candidate_module
from business.models import BusinessUser
from beta_invite.models import Campaign
from beta_invite.util import email_sender
from dashboard.models import Candidate


def get_campaign_for_dashboard(request, business_user):

    campaign_id = request.GET.get('campaign_id')
    if campaign_id:
        return Campaign.objects.get(pk=campaign_id)
    # default campaign
    else:
        return business_user.campaigns.all()[0]


def get_dashboard_params(campaign):

    params, states = candidate_module.get_rendering_data(campaign.id)

    # State Backlog and Prospect will show as one.
    params['backlog'] += params['prospect']
    params['waiting_for_interview'] += params['did_interview']
    params['rejected'] += params['failed_tests']
    params['sent_to_client'] += params['got_the_job']
    params['campaign'] = campaign

    return params


def get_business_user_and_campaign(request, pk):
    business_user = BusinessUser.objects.get(pk=pk)
    campaign = get_campaign_for_dashboard(request, business_user)
    return business_user, campaign


def get_checked_box_candidates(campaign_id, request):
    candidates = Candidate.objects.filter(campaign_id=campaign_id)
    return [c for c in candidates if request.GET.get('{}_checkbox'.format(c.id))]


def send_email_from_dashboard(request, campaign):

    # enters here when sending an email
    if request.GET.get('send_mail') is not None:

        candidates = get_checked_box_candidates(campaign.id, request)

        email_sender.send(objects=candidates,
                          language_code='es',
                          body_input=request.GET.get('email_body'),
                          subject=request.GET.get('email_subject'),
                          with_localization=False,
                          body_is_filename=False)
