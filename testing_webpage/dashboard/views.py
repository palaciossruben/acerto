import json
import common
from django.core import serializers
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Q
from django.http import HttpResponse

from beta_invite.models import Campaign, Test, TestType, BulletType, Interview, Survey, Bullet, QuestionType, Question, Answer
from dashboard.models import Candidate, Message, Screening
from dashboard import constants as cts
from beta_invite.util import email_sender
from beta_invite.views import get_drop_down_values
from dashboard import interview_module, candidate_module, campaign_module, test_module
from match import model
from business import dashboard_module
from business.models import BusinessUser
import business


CANDIDATE_FORECAST_LIMIT = 10


def index(request):
    """
    Args:
        request: HTTP
    Returns: renders main view with a list of campaigns
    """

    campaigns = Campaign.objects.filter(removed=False).order_by('-active', 'name', 'title_es')

    for campaign in campaigns:
        common.calculate_operational_efficiency(campaign)

    return render(request, cts.MAIN_DASHBOARD, {'campaigns': campaigns,
                                                'tests': Test.get_all()})


# ------------------------------- CAMPAIGN -------------------------------


def add_to_message_queue(candidates, text):
    """
    Adds objects to the message table. So later on this table will serve as a message queue.
    :param candidates: list of candidates.
    :param text: string
    :return: writes on table messages to be sent.
    """
    for candidate in candidates:
        Message(candidate=candidate, text=text).save()


def update_candidate_forecast():
    """
    Updates up to CANDIDATE_FORECAST_LIMIT per execution, due to time limit on production server, and possible crush.
    :return: updates.
    """
    candidates = [c for c in Candidate.objects.filter(Q(match_regression=None) | Q(match_classification=None))]
    candidates = candidates[:min(len(candidates), CANDIDATE_FORECAST_LIMIT)]
    model.predict_match_and_save(candidates, regression=False)


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

        candidates = candidate_module.get_checked_box_candidates(pk, request)

        email_sender.send(objects=candidates,
                          language_code=request.LANGUAGE_CODE,
                          body_input=request.POST.get('email_body'),
                          subject=candidate_module.get_subject(request, pk),
                          with_localization=False,
                          body_is_filename=False)

    if request.POST.get('send_message') is not None:
        candidates = candidate_module.get_checked_box_candidates(pk, request)
        add_to_message_queue(candidates, request.POST.get('email_body'))

    #update_candidate_forecast()

    params, states = candidate_module.get_rendering_data(pk)

    # all campaigns except the current one.
    campaigns_to_move_to = Campaign.objects.exclude(pk=pk)

    params['states'] = states
    params['campaign_id'] = pk
    params['screenings'] = [s for s in Screening.objects.all()]
    params['campaigns'] = campaigns_to_move_to
    params['current_campaign'] = Campaign.objects.get(pk=pk)

    return render(request, cts.EDIT_CANDIDATES, params)


def new_campaign(request):

    countries, cities, education, professions, work_areas, genders = get_drop_down_values(request.LANGUAGE_CODE)
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

    campaign_module.create_campaign(request)

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
    countries, cities, education, professions, work_areas, genders = get_drop_down_values(request.LANGUAGE_CODE)

    return render(request, cts.NEW_OR_EDIT_CAMPAIGN, {'countries': countries,
                                                      'cities': cities,
                                                      'education': education,
                                                      'professions': professions,
                                                      'work_areas': work_areas,
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


def delete_campaign(request, pk):

    campaign = Campaign.objects.get(pk=pk)

    if campaign:
        campaign.removed = True
        campaign.save()

    return redirect('/dashboard')


# ------------------------------- CAMPAIGN TESTS -------------------------------


def tests(request, pk):
    """
    Args:
        request: HTTP
        pk: campaign_id
    Returns: Renders the list of tests for a given campaign
    """
    campaign = Campaign.objects.get(pk=pk)

    return render(request, cts.TESTS, {'campaign': campaign,
                                       'tests': Test.get_all()})


def add_test(request, pk):
    """
    Args:
        request: HTTP
        pk: campaign_id
    Returns: adds a new test to a given campaign
    """
    campaign = Campaign.objects.get(pk=pk)
    new_test_id = int(request.POST.get('new_test_id'))
    campaign.tests.add(new_test_id)
    campaign.save()

    return redirect('/dashboard/campaign/{}/tests'.format(campaign.id))


def delete_test(request, pk):
    """
    Args:
        request: HTTP
        pk: campaign_id
    Returns: adds a new test to a given campaign
    """
    campaign = Campaign.objects.get(pk=pk)
    new_test_id = int(request.POST.get('test_id'))
    campaign.tests.remove(new_test_id)
    campaign.save()

    return redirect('/dashboard/campaign/{}/tests'.format(campaign.id))


# ------------------------------- TESTS -------------------------------


def delete_question(request):

    question_id = int(request.POST.get('question_id'))
    Question.objects.get(pk=question_id).delete()

    return HttpResponse('')


def delete_answer(request):

    answer_id = int(request.POST.get('answer_id'))
    Answer.objects.get(pk=answer_id).delete()

    return HttpResponse('')


def edit_test(request, pk):
    """
    :param request: http
    :param pk: test_id
    :return: render
    """

    test_types = TestType.objects.all()
    question_types = QuestionType.objects.all()
    question_types_json = serializers.serialize("json", question_types)

    # TODO: to fix fixture inconsistencies. Can be removed later
    test = Test.objects.get(pk=pk)
    test.remove_question_gaps()
    for question in test.questions.all():
        question.remove_answer_gaps()

    return render(request, cts.EDIT_TEST, {'test_types': test_types,
                                           'question_types': question_types,
                                           'question_types_json': question_types_json,
                                           'test': test})


def update_test(request, pk):
    """
    Args:
        request: HTTP
    Returns: redirects to dashboard after updating new test.
    """

    test = Test.objects.get(pk=pk)
    test.type_id = int(request.POST.get('test_type_id'))
    test.name = request.POST.get('name')
    test.name_es = request.POST.get('name_es')
    test.cut_score = int(request.POST.get('cut_score'))
    test.feedback_url = request.POST.get('feedback_url')
    test.excluding = bool(request.POST.get('excluding'))

    test.save()  # save first, for saving questions

    test = test_module.update_test_questions(test, request)
    test.save()

    return redirect('/dashboard/test/{}'.format(pk))


def duplicate_test(request, pk):
    """
    Args:
        request: HTTP
    Returns: redirects to dashboard after duplicating test.
    """

    test = Test.objects.get(pk=pk)
    test.duplicate()

    return redirect('/dashboard')


def new_test(request):
    """
    Called to display a new test form
    :param request:
    :return:
    """

    test_types = TestType.objects.all()
    question_types = QuestionType.objects.all()
    question_types_json = serializers.serialize("json", question_types)

    return render(request, cts.NEW_TEST, {'test_types': test_types,
                                          'question_types': question_types,
                                          'question_types_json': question_types_json
                                          })


def save_test(request):
    """
    Saves a new test
    Args:
        request: HTTP
    Returns: redirects to dashboard after saving new test.
    """
    test = Test(type_id=int(request.POST.get('test_type_id')),
                name=request.POST.get('name'),
                name_es=request.POST.get('name_es'),
                cut_score=int(request.POST.get('cut_score')),
                feedback_url=request.POST.get('feedback_url'),
                excluding=bool(request.POST.get('excluding')))
    test.save()  # save first, for saving questions

    test = test_module.update_test_questions(test, request)
    test.save()

    return redirect('/dashboard/test/{}'.format(test.pk))


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


def mark_as_added(users):
    """
    Flag added to True value.
    :param users: collection
    :return: none
    """
    for u in users:
        u.added = True
        u.save()


def send_new_contacts(request):
    """
     Works as API for auto-messenger app
     If there is a problem adding contacts on the app possible solution is:

     1. Uncomment line 542 [:50] part, this will limit number of candidates added and publish API
     2. Run app to add those 50 contacts
     2. Run bot and send messages from those 50 candidates
     3. Run the app again, add another 50
     4. Repeat until no more messages are sent.
    :param request: HTTP
    :return: json
    """

    users = {m.candidate.user for m in Message.objects.filter(~Q(candidate__user__phone=None),
                                                              sent=False)}  # [:50]

    for u in users:
        u.change_to_international_phone_number()
        u.name = email_sender.remove_accents(u.name)

    #json_data = serializers.serialize('json', users)

    mark_as_added(users)

    json_data = json.dumps([{'pk': u.pk, 'fields': {'phone': u.phone, 'name': u.name, 'email': u.email}} for u in users])

    return JsonResponse(json_data, safe=False)


def send_messages(request):
    """
    Sends the messages and their respective users.
    :param request: HTTP
    :return: json
    """

    messages = [m.add_format_and_mark_as_sent() for m in Message.objects.filter(sent=False,
                                                                                candidate__user__added=True)]

    messages_json = serializers.serialize('json', messages)

    return JsonResponse(messages_json, safe=False)


def business_dashboard(request, pk):
    """
    Same endpoint as the dashboard but for admin access, with no login
    :param request: HTTP
    :param pk: THIS IS DIFFERENT FROM BUSINESS IMPLEMENTATION, here it is the campaign_id,
    while in production it is the business_user_id
    :return: renders view.
    """

    campaign = Campaign.objects.get(pk=pk)

    dashboard_module.send_email_from_dashboard(request, campaign)

    query = BusinessUser.objects.filter(campaigns__contains=campaign)
    user = [id for id in query.all()[0]]
    business_user_id = user.id

    return render(request, business.constants.DASHBOARD_VIEW_PATH, dashboard_module.get_dashboard_params(campaign))
