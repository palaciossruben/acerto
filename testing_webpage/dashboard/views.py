import datetime
from django.core import serializers
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

import basic_common
import common
from beta_invite.util import common_senders
from beta_invite import constants as beta_cts
from beta_invite.models import Campaign, Test, TestType, BulletType, Interview, Survey, Bullet, QuestionType, Question, Answer, CampaignState, CampaignMessage
from business.models import Company
from dashboard.models import Candidate, Message, Screening
from dashboard import constants as cts
from beta_invite.util import email_sender, messenger
from beta_invite.views import get_drop_down_values
from dashboard import interview_module, candidate_module, campaign_module, test_module
from match import model
from api.models import LeadMessage
from testing_webpage.models import CampaignPendingEmail, EmailType

CANDIDATE_FORECAST_LIMIT = 20


@login_required
def index(request):
    """
    Args:
        request: HTTP
    Returns: renders main view with a list of campaigns
    """

    # TODO: this basic login... works but the real admin users can be used instead
    # TODO: how to add the same auth to all the app????
    if basic_common.not_admin_user(request):
        return redirect('business:login')
    campaigns = Campaign.objects.filter(removed=False).order_by('-created_at', 'state', 'title_es').all()

    for campaign in campaigns:
        common.calculate_operational_efficiency(campaign)

    return render(request, cts.MAIN_DASHBOARD, {'campaigns': campaigns})

# ------------------------------- CAMPAIGN -------------------------------


def tests_list(request):
    """
    :param request: HTTP request
    :return: render view
    """

    tests = Test.get_all()

    return render(request, cts.TEST_LIST, {'tests': tests})


def candidate_detail(request, candidate_id):
    """
    :param request: HTTP request
    :param candidate_id: int Candidate id
    :return: render view
    """
    return render(request, cts.CANDIDATE_DETAIL, {'candidate': Candidate.objects.get(pk=candidate_id)})


def add_to_message_queue(candidates, text):
    """
    Adds objects to the message table. So later on this table will serve as a message queue.
    :param candidates: list of candidates.
    :param text: string
    :return: writes on table messages to be sent.
    """
    for candidate in candidates:
        Message(candidate=candidate, text=text).save()


def update_candidate_forecast(campaign):
    """
    Updates up to CANDIDATE_FORECAST_LIMIT per execution, due to time limit on production server, and possible crash.
    :return: updates.
    """
    candidates = Candidate.objects.filter(Q(match_classification=None) & Q(campaign=campaign)).all()
    candidates = candidates[:min(len(candidates), CANDIDATE_FORECAST_LIMIT)]
    model.predict_match_and_save(candidates)


# TODO: use Ajax to optimize rendering. Has no graphics therefore is very low priority.
def edit_campaign_candidates(request, campaign_id):
    """
    Args:
        request: HTTP
        campaign_id: campaign primary key
    Returns: This controls the candidates dashboard
    """
    campaign = Campaign.objects.get(pk=campaign_id)

    action = request.POST.get('action')
    candidate_id = request.POST.get('candidate_id')
    if candidate_id is not None:
        candidate = Candidate.objects.get(pk=int(candidate_id))

        if action == 'update':
            candidate_module.update_candidate_manually(request, candidate)
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

        candidates = candidate_module.get_checked_box_candidates(campaign_id, request)

        email_sender.send(objects=candidates,
                          language_code=request.LANGUAGE_CODE,
                          body_input=request.POST.get('email_body'),
                          subject=candidate_module.get_subject(request, campaign_id),
                          with_localization=False,
                          body_is_filename=False)

    if request.POST.get('send_message') is not None:
        candidates = candidate_module.get_checked_box_candidates(campaign_id, request)
        add_to_message_queue(candidates, request.POST.get('email_body'))

    update_candidate_forecast(campaign)

    params, states = candidate_module.get_rendering_data(campaign_id)

    # all campaigns except the current one.
    campaigns_to_move_to = Campaign.objects.exclude(pk=campaign_id)

    params['states'] = states
    params['campaign_id'] = campaign_id
    params['screenings'] = [s for s in Screening.objects.all()]
    params['campaigns'] = campaigns_to_move_to
    params['current_campaign'] = Campaign.objects.get(pk=campaign_id)

    return render(request, cts.EDIT_CANDIDATES, params)


def new_campaign(request):

    countries, cities, education, professions, work_areas, genders = get_drop_down_values(request.LANGUAGE_CODE)
    bullet_types_json = serializers.serialize("json", BulletType.objects.all())

    return render(request, cts.NEW_OR_EDIT_CAMPAIGN, {'countries': countries,
                                                      'education': education,
                                                      'professions': professions,
                                                      'bullet_types_json': bullet_types_json,
                                                      'action_url': '/dashboard/campaign/create',
                                                      'title': 'Nueva Campaña',
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


def edit_campaign(request, campaign_id):
    """
    Args:
        request: HTTP
        campaign_id: campaign_id
    Returns: Renders basic properties of a campaign
    """
    campaign = Campaign.objects.get(pk=campaign_id)
    countries, cities, education, professions, work_areas, genders = get_drop_down_values(request.LANGUAGE_CODE)
    business_user = common.get_business_user_with_campaign(campaign)
    if not business_user:
        company = ""
    else:
        company = business_user.company

    return render(request, cts.NEW_OR_EDIT_CAMPAIGN, {'countries': countries,
                                                      'cities': cities,
                                                      'education': education,
                                                      'professions': professions,
                                                      'work_areas': work_areas,
                                                      'campaign': campaign,
                                                      'action_url': '/dashboard/campaign/update_basic_properties',
                                                      'title': 'Update {}'.format(campaign.title_es),
                                                      'campaign_states': CampaignState.objects.all(),
                                                      'company': company
                                                      })


def send_feedback_message_and_mail(business_user, campaign, request):

    # goes from active to finish, will ask for feedback
    if campaign.state == CampaignState.objects.get(code='A') and \
                    int(request.POST.get('state_id')) == CampaignState.objects.get(code='F').id:

        # TODO: this is really wrong
        CampaignPendingEmail.add_to_queue(the_objects=campaign,
                                          language_code='es',
                                          body_input='business_feedback',
                                          subject='Publicación terminada {campaign}',
                                          email_type=EmailType.objects.get(name='business_feedback'))
        messenger.send(objects=campaign,
                       language_code='es',
                       body_input='business_feedback')


def update_basic_properties(request):
    """
    Args:
        request: HTTP.
    Returns: Updates just the basics of a campaign.
    """
    campaign = common.get_campaign_from_request(request)
    business_user = common.get_business_user_with_campaign(campaign)

    send_feedback_message_and_mail(business_user, campaign, request)

    campaign_module.update_campaign_basic_properties(campaign, request)
    if business_user:
        company = business_user.company
        if company:
            company.name = request.POST.get('company')
            company.save()
        else:
            company = Company()
            company.name = request.POST.get('company')
            company.save()
            business_user.company = company
            business_user.save()
    else:
        pass

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
    test.public = bool(request.POST.get('public'))

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


def mark_as_added(objects):
    """
    Flag added to True value.
    :param objects: collection
    :return: none
    """
    for o in objects:
        o.added = True
        o.save()


def get_candidate_users():

    users = [m.candidate.user for m in Message.objects.filter(~Q(candidate__user__phone=None),
                                                              sent=False)]

    for u in users:
        u.change_to_international_phone_number(add_plus=True)
        u.name = email_sender.remove_accents(u.name)

    mark_as_added(users)

    return users


def get_leads():
    leads = {m.lead for m in LeadMessage.objects.filter(~Q(lead__phone=None),
                                                        sent=False)}

    for l in leads:
        l.change_to_international_phone_number()
        l.name = email_sender.remove_accents(l.name)

    mark_as_added(leads)

    return list(leads)


def get_business_users():
    """
    Gets the business_users from messages sending to campaigns
    :return:
    """
    campaigns = {m.campaign for m in CampaignMessage.objects.filter(sent=False)}
    mark_as_added(campaigns)

    business_users = []
    for campaign in campaigns:
        business_user = common.get_business_user_with_campaign(campaign)
        if business_user and business_user.phone:
            business_user.change_to_international_phone_number(campaign)
            business_user.name = email_sender.remove_accents(business_user.name)
            business_users.append(business_user)

    return list(business_users)


def add_backlog_messages(message_filename):

    # TODO: add English
    candidates = [c for c in
                  Candidate.objects.filter(Q(created_at__gt=datetime.datetime.today() - datetime.timedelta(days=5)) &
                                           Q(state__code='BL') &
                                           Q(campaign__state__name='Active') &
                                           ~Q(message__filename=message_filename) &
                                           ~Q(campaign__tests=None) &
                                           ~Q(campaign_id=beta_cts.DEFAULT_CAMPAIGN_ID))]

    messenger.send(objects=candidates,
                   language_code='es',
                   body_input=message_filename)


def add_external_job_exchange_messages(message_filename):
    # TODO: add English
    candidates = [c for c in
                  Candidate.objects.filter(Q(created_at__gt=datetime.datetime.today() - datetime.timedelta(days=5)) &
                                           Q(state__code='BL') &
                                           Q(campaign__state__name='Active') &
                                           Q(campaign__tests=None) &
                                           ~Q(message__filename=message_filename) &
                                           ~Q(campaign_id=beta_cts.DEFAULT_CAMPAIGN_ID))]

    messenger.send(objects=candidates,
                   language_code='es',
                   body_input=message_filename)


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

    add_backlog_messages('candidate_backlog')
    add_external_job_exchange_messages('external_job_exchange')

    leads = get_leads()
    users = get_candidate_users()
    business_users = get_business_users()

    list_of_users = [{'pk': u.pk, 'fields': {'phone': u.phone, 'name': u.name, 'email': u.email}} for u in users + leads + business_users]

    return JsonResponse(list_of_users, safe=False)


def add_contact_name(campaign_messages):

    for m in campaign_messages:

        business_user = common.get_business_user_with_campaign(m.campaign)
        name = business_user.name if business_user else ''

        m.contact_name = '{name} {pk}'.format(name=name,
                                              pk=str(m.campaign.pk))

    return campaign_messages


def send_messages(request):
    """
    Sends the messages and their respective users.
    :param request: HTTP
    :return: json
    """

    lead_messages = [
        m.add_format_and_mark_as_sent({'name': common_senders.get_first_name(m.lead.name)})
        for m in LeadMessage.objects.filter(sent=False, lead__added=True)
    ]

    messages = [
        m.add_format_and_mark_as_sent(common_senders.get_params_with_candidate(m.candidate,
                                                                               m.candidate.user.language_code,
                                                                               {}))
        for m in Message.objects.filter(sent=False, candidate__user__added=True)
    ]

    campaign_messages = [
        m.add_format_and_mark_as_sent(common_senders.get_params_with_campaign(m.campaign))
        for m in CampaignMessage.objects.filter(sent=False, campaign__added=True)
    ]
    campaign_messages = add_contact_name(campaign_messages)

    messages_json = serializers.serialize('json', messages + lead_messages + campaign_messages)

    return JsonResponse(messages_json, safe=False)
