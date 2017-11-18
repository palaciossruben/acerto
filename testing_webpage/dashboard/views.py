
import common
from django.core import serializers
from django.shortcuts import render, redirect
from beta_invite.models import Campaign, User, Evaluation, Test, BulletType, Interview, Question, Survey, Bullet
from dashboard.models import State, Candidate, Comment
from dashboard import constants as cts
from beta_invite.util import email_sender
from beta_invite.views import get_drop_down_values
from dashboard import interview_module, candidate_module, campaign_module


def index(request):
    """
    Args:
        request: HTTP
    Returns: renders main view with a list of campaigns
    """
    campaigns = Campaign.objects.all()
    tests = Test.objects.all()
    return render(request, cts.MAIN_DASHBOARD, {'campaigns': campaigns,
                                                'tests': tests})


# ------------------------------- CAMPAIGN -------------------------------


# TODO: use Ajax to optimize rendering. Has no graphics therefore is very low priority.
def edit_campaign_candidates(request, pk):
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
            candidate_module.update_candidate(request, candidate)
        elif action == 'add':
            candidate_module.add_candidate_to_campaign(request, candidate)
        elif action == 'remove':
            candidate_module.remove_candidate(candidate)
        elif action == 'move':
            if candidate_module.add_candidate_to_campaign(request, candidate):  # only erase if has add successfully
                candidate_module.remove_candidate(candidate)

    # TODO: can be done with JS in smarter way???
    # enters here when sending an email
    if request.POST.get('send_mail') is not None:

        users = candidate_module.get_checked_box_users(pk, request)

        email_sender.send(users=users,
                          language_code=request.LANGUAGE_CODE,
                          body_input=request.POST.get('email_body'),
                          subject=candidate_module.get_subject(request, pk),
                          with_localization=False,
                          body_is_filename=False)

    backlog, waiting_tests, waiting_interview, did_interview_in_standby, sent_to_client, got_job, rejected, states = candidate_module.get_rendering_data(pk)

    # all campaigns except the current one.
    campaigns_to_move_to = Campaign.objects.exclude(pk=pk)

    return render(request, cts.EDIT_CANDIDATES, {'states': states,
                                                 'campaign_id': pk,
                                                 'backlog': backlog,
                                                 'waiting_tests': waiting_tests,
                                                 'waiting_interview': waiting_interview,
                                                 'did_interview_in_standby': did_interview_in_standby,
                                                 'sent_to_client': sent_to_client,
                                                 'got_job': got_job,
                                                 'rejected': rejected,
                                                 'campaigns': campaigns_to_move_to,
                                                 'current_campaign': Campaign.objects.get(pk=pk)
                                                 })


def new_campaign(request):

    countries, education, professions = get_drop_down_values(request.LANGUAGE_CODE)
    bullet_types_json = serializers.serialize("json", BulletType.objects.all())

    return render(request, cts.NEW_OR_EDIT_CAMPAIGN, {'countries': countries,
                                                      'education': education,
                                                      'professions': professions,
                                                      'bullet_types_json': bullet_types_json,
                                                      'action_url': '/dashboard/campaign/create',
                                                      'title': 'New Campaign',
                                                      })


def create_campaign(request):
    """
    When you are in a new campaign and you save the model
    Args:
        request: HTTP
    Returns:
    """

    # saves to create id first.
    campaign = Campaign()
    campaign.save()

    campaign_module.update_campaign_basic_properties(campaign, request)
    campaign_module.update_campaign_bullets(campaign, request)

    # in this specific case gotta go back. Because if the user stays modifying the campaign on the 'new' template it
    # will create additional campaigns instead of modifying the first creation.
    return redirect('/dashboard')


def edit_campaign(request, pk):
    """
    Args:
        request: HTTP
        pk: campaign_id
    Returns: Renders basic properties of a campaign
    """
    campaign = Campaign.objects.get(pk=pk)
    countries, education, professions = get_drop_down_values(request.LANGUAGE_CODE)

    return render(request, cts.NEW_OR_EDIT_CAMPAIGN, {'countries': countries,
                                                      'education': education,
                                                      'professions': professions,
                                                      'campaign': campaign,
                                                      'action_url': '/dashboard/campaign/update_basic_properties',
                                                      'title': 'Update Campaign',
                                                      })


def update_basic_properties(request):
    """
    Args:
        request: HTTP.
    Returns: Updates just the basics of a campaign.
    """
    campaign = common.get_campaign_from_request(request)

    campaign_module.update_campaign_basic_properties(campaign, request)

    return campaign_module.get_campaign_edit_url(campaign)


# ------------------------------- TESTS -------------------------------


def edit_test():
    # TODO: implement
    pass


def new_test(request):
    # TODO: implement
    return render(request, cts.NEW_TEST, {})


# ------------------------------- BULLETS -------------------------------


def bullets(request, pk):
    """
    Args:
        request: HTTP
        pk: campaign_id
    Returns: Renders list of all bullets.
    """
    campaign = Campaign.objects.get(pk=pk)

    bullet_types = BulletType.objects.all()
    bullet_types_json = serializers.serialize("json", bullet_types)

    return render(request, cts.BULLETS, {'bullet_types': bullet_types,
                                         'bullet_types_json': bullet_types_json,
                                         'campaign': campaign,
                                         })


def update_bullets(request):
    """
    Args:
        request: HTTP.
    Returns: Updates just the basics of a campaign.
    """
    campaign = common.get_campaign_from_request(request)

    campaign_module.update_campaign_bullets(campaign, request)

    return campaign_module.get_bullets_url(campaign)


def delete_bullet(request):
    """
    Args:
        request: HTTP
    Returns:
    """
    bullet_id = int(request.POST.get('bullet_id'))
    bullet = Bullet.objects.get(pk=bullet_id)

    campaign = common.get_campaign_from_request(request)

    campaign.bullets.remove(bullet)
    campaign.save()

    return campaign_module.get_bullets_url(campaign)


# ------------------------------- INTERVIEW -------------------------------


def interview(request, pk):
    """
    Args:
        request: HTTP
        pk: campaign_id
    Returns: Updates changes to the Questions of a Interview. And renders those questions.
    """

    interview_name = request.POST.get('interview_name')
    interview_name_es = request.POST.get('interview_name_es')

    campaign = Campaign.objects.get(pk=pk)

    # if no interview, then it creates a new one.
    if len(campaign.interviews.all()) == 0:

        interview_obj = Interview(name=interview_name,
                                  name_es=interview_name_es)
        interview_obj.save()  # saves to get the id. Cannot add questions without having an id.

        campaign.interviews = [interview_obj]
        campaign.save()

    else:  # there is already an interview.
        # TODO: change this when a campaign has more than 1 interview.
        interview_obj = campaign.interviews.all()[0]

    return render(request, cts.INTERVIEW_QUESTIONS, {'campaign': campaign,
                                                     'questions': [q for q in interview_obj.questions.order_by('order').all()],
                                                     'ziggeo_api_key': common.get_ziggeo_api_key()
                                                     })


def create_interview_question(request):
    """
    Given a new_token_id and texts, it creates a new question.
    Args:
        request: HTTP
    Returns: Renders the same view that it came from.
    """
    campaign = common.get_campaign_from_request(request)

    interview_module.create_question(request, campaign)

    # goes back to original page.
    return interview_module.get_redirect_url(campaign.id)


def update_interview_question(request):
    """
    Updates a interview question.
    Args:
        request: HTTP
    Returns: Save info and redirects back to interviews.
    """

    campaign = common.get_campaign_from_request(request)

    interview_module.update_question(request)

    # goes back to original page.
    return interview_module.get_redirect_url(campaign.id)


def delete_interview_question(request):
    """
    Args:
        request: HTTP
    Returns: Delete question and redirects back to interviews.
    """

    campaign = common.get_campaign_from_request(request)

    interview_module.delete_question(request, campaign)

    # goes back to original page.
    return interview_module.get_redirect_url(campaign.id)


def edit_intro_video(request):
    """
    Edits the intro video of the interview.
    Args:
        request: HTTP
    Returns: Render view.
    """
    new_video = request.POST.get('new_video')
    if new_video is not None:
        common.set_intro_video(new_video)

    return render(request, cts.EDIT_INTRO_VIDEO, {'current_video': common.get_intro_video(),
                                                  'ziggeo_api_key': common.get_ziggeo_api_key()})


def check_interview(request):
    """
    Args:
        request: HTTP
    Returns: Renders the whole interview for a given candidate.
    """

    candidate = Candidate.objects.get(pk=request.GET.get('candidate_id'))
    surveys = Survey.objects.filter(user=candidate.user,
                                    campaign=candidate.campaign,
                                    video_token__isnull=False,
                                    interview__isnull=False).all()

    return render(request, cts.INTERVIEW, {'ziggeo_api_key': common.get_ziggeo_api_key(),
                                           'question_answer_tuples': interview_module.get_sorted_tuples(surveys)})
