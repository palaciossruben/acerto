import re

import common
from django.core import serializers
from django.shortcuts import render, redirect
from beta_invite.models import Campaign, User, Evaluation, Test, BulletType, Bullet, Interview, Question, Survey
from dashboard.models import State, Candidate, Comment
from dashboard import constants as cts
from beta_invite.util import email_sender
from beta_invite.views import save_curriculum_from_request, get_drop_down_values
from dashboard import interview_module


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
    This only applies for new users that come from BL or WFT
    Args:
        candidate: Object
        user: Object
    Returns: None, just updates
    """

    if len(user.evaluations.all()) > 0 and candidate.state.code in ['BL', 'WFT']:

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
    Returns: Boolean indicating whether a new candidate was added
    """

    # Updates latest changes, first.
    update_candidate(request, candidate)

    selected_campaign_id = int(request.POST.get('{}_selected_campaign'.format(candidate.id)))

    if selected_campaign_id == cts.CAMPAIGN_ID_NULL or user_in_campaign(candidate.user_id, selected_campaign_id):
        return False
    else:
        new_candidate = Candidate(user_id=candidate.user_id,
                                  campaign_id=selected_campaign_id,
                                  state=candidate.state,
                                  comment=candidate.comment)
        user = new_candidate.user
        user.campaign_id = selected_campaign_id
        user.save()
        new_candidate.save()
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
    did_interview_in_standby = get_candidates_from_state('DIS', campaign_id)
    sent_to_client = get_candidates_from_state('STC', campaign_id)
    got_job = get_candidates_from_state('GTJ', campaign_id)

    rejected_candidates = Candidate.objects.filter(campaign_id=campaign_id,
                                                   state__is_rejected=True,
                                                   removed=False).order_by('-state__priority')

    return backlog, waiting_tests, waiting_interview, did_interview_in_standby, sent_to_client, got_job, rejected_candidates, State.objects.all()


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

        # Erasing the old comment field is done for retro-compatibility purposes only.
        candidate.comment = ''

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

    backlog, waiting_tests, waiting_interview, did_interview_in_standby, sent_to_client, got_job, rejected, states = get_rendering_data(pk)

    # all campaigns except the current one.
    campaigns_to_move_to = Campaign.objects.exclude(pk=pk)

    return render(request, cts.DASHBOARD_EDIT, {'states': states,
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


def edit_test():
    # TODO: implement
    pass


def new_test(request):
    # TODO: implement
    return render(request, cts.NEW_TEST, {})


def new_campaign(request):

    countries, education, professions = get_drop_down_values(request.LANGUAGE_CODE)
    bullet_types_json = serializers.serialize("json", BulletType.objects.all())

    return render(request, cts.NEW_CAMPAIGN, {'countries': countries,
                                              'education': education,
                                              'professions': professions,
                                              'bullet_types_json': bullet_types_json,
                                              'action_url': 'create',
                                              'title': 'New Campaign',
                                              })


def update_bullet_attr(campaign, dict_id, key_bullet_dict, value, attribute_name):
    """
    Uses meta-programing, and updates or creates new Bullet objects.
    Args:
        campaign: Object
        dict_id: temporal id to distinguish between different new ids only.
        key_bullet_dict: dictionary containing new stored bullets to add.
        value:
        attribute_name: the name of the Bullet object attribute.
    Returns: None, just update
    """
    if dict_id in key_bullet_dict.keys():  # Updates bullet.
        b = key_bullet_dict[dict_id]
        setattr(b, attribute_name, value)
        b.save()
    else:  # creates new Bullet
        b = Bullet(**{attribute_name: value})
        b.save()
        key_bullet_dict[dict_id] = b
        campaign.bullets.add(b)


def update_campaign(campaign, request):
    """
    Args:
        campaign: Campaign Object
        request: HTTP request
    Returns: None, just updates the campaign object.
    """
    key_bullet_dict = {}
    for key, value in request.POST.items():

        if hasattr(Campaign, key):
            setattr(campaign, key, value)

        # When there is a new_bullet.
        elif 'new_bullet' in key:

            dict_id = int(re.findall('^\d+', key)[0])

            if 'type' in key:
                update_bullet_attr(campaign, dict_id, key_bullet_dict, value, 'bullet_type_id')

            elif re.match(r'.*bullet_name$', key):
                update_bullet_attr(campaign, dict_id, key_bullet_dict, value, 'name')

            elif re.match(r'.*bullet_name_es$', key):
                update_bullet_attr(campaign, dict_id, key_bullet_dict, value, 'name_es')

        # updates existing bullets
        elif re.search('\d+_bullet', key):

            # gets the bullet id.
            bullet_pk = int(re.findall(r'\d+', key)[0])
            bullet = Bullet.objects.get(pk=bullet_pk)

            if 'type' in key:
                bullet.bullet_type_id = value

            elif re.match(r'.*bullet_name$', key):
                bullet.name = value

            elif re.match(r'.*bullet_name_es$', key):
                bullet.name_es = value

            bullet.save()

    campaign.save()


def create_campaign(request):

    # saves to create id first.
    campaign = Campaign()
    campaign.save()

    update_campaign(campaign, request)

    return redirect('../')


def edit_campaign(request, pk):

    campaign = Campaign.objects.get(pk=pk)

    if request.method == "POST":
        update_campaign(campaign, request)

    countries, education, professions = get_drop_down_values(request.LANGUAGE_CODE)
    bullet_types = BulletType.objects.all()
    bullet_types_json = serializers.serialize("json", bullet_types)

    return render(request, cts.NEW_CAMPAIGN, {'countries': countries,
                                              'education': education,
                                              'professions': professions,
                                              'bullet_types': bullet_types,
                                              'bullet_types_json': bullet_types_json,
                                              'campaign': campaign,
                                              'action_url': '#',
                                              'title': 'Update Campaign',
                                              })


def interview(request, pk):

    new_video_token = request.POST.get('new_video_token')
    new_question_text = request.POST.get('new_question_text')
    new_question_text_es = request.POST.get('new_question_text_es')
    interview_name = request.POST.get('interview_name')
    interview_name_es = request.POST.get('interview_name_es')

    campaign = Campaign.objects.get(pk=pk)

    new_question = interview_module.get_new_question(new_question_text, new_question_text_es, new_video_token)

    # if no interview, then it creates a new one.
    if len(campaign.interviews.all()) == 0:

        interview_obj = Interview(name=interview_name,
                                  name_es=interview_name_es)
        interview_obj.save()  # saves to get the id. Cannot add questions without having an id.

        if new_question is not None:
            interview_obj.questions.add(new_question)

        interview_obj.save()  # saves to add the questions.

        campaign.interviews = [interview_obj]
        campaign.save()

    else:  # there is already an interview.

        # TODO: change this when a campaign has more than 1 interview.
        interview_obj = campaign.interviews.all()[0]
        if new_question is not None:
            interview_module.assign_order_to_question(new_question, interview_obj)
            interview_obj.questions.add(new_question)

        interview_obj.save()

        interview_module.update_old_question_statements(request, interview_obj, new_question)

    return render(request, cts.INTERVIEW_QUESTIONS, {'questions': [q for q in interview_obj.questions.order_by('order').all()],
                                                     'ziggeo_api_key': common.get_ziggeo_api_key()
                                                     })


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


def get_sorted_tuples(surveys):
    """
    Args:
        surveys: Survey Objects.
    Returns: (Question, Survey) tuples. Sorted by Question.order
    """
    question_answer_tuples = zip([s.question for s in surveys], surveys)
    return sorted(question_answer_tuples, key=lambda my_tuple: my_tuple[0].order)


def check_interview(request):
    """
    Args:
        request: HTTP
    Returns: Renders the whole interview.
    """

    candidate = Candidate.objects.get(pk=request.GET.get('candidate_id'))
    surveys = Survey.objects.filter(user=candidate.user, campaign=candidate.campaign).all()

    return render(request, cts.INTERVIEW, {'ziggeo_api_key': common.get_ziggeo_api_key(),
                                           'question_answer_tuples': get_sorted_tuples(surveys)})
