"""
This is a helper module for the interview.
"""

from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist

import common
from beta_invite.models import Survey
from dashboard.models import Candidate, State


def on_last_question(interview_obj, question):
    """
    Args:
        interview_obj: Interview Object
        question: Question object, currently being asked
    Returns: Boolean indicating if it is on the last question.
    """
    last_question_number = max({q.order for q in interview_obj.questions.all()})
    return last_question_number == question.order


def get_right_button_text(interview_obj, question):
    return _('Finish Interview') if on_last_question(interview_obj, question) else _('Save and continue')


def has_interview(campaign):
    """
    Args:
        campaign:
    Returns:
    """

    # TODO: designed with campaigns having only 1 interview.
    if campaign.interviews is not None:
        interviews = campaign.interviews.all()
        if len(interviews) > 0:
            interview_obj = interviews[0]
            if interview_obj.questions is not None:
                questions = interview_obj.questions.all()
                return len(questions) > 0

    return False


def get_previous_url(question_number, campaign_id, user_id):
    """
    Args:
        question_number: int with the interview question number.
    Returns: string with url
    """

    if question_number > 1:
        return adds_campaign_and_user_to_url(str(question_number - 1), user_id, campaign_id)
    else:
        return adds_campaign_and_user_to_url('../test_result', user_id, campaign_id)


def fetch_current_video_answer(campaign, user, question):
    """
    Fetches the latest video for a given user and question.
    Args:
        campaign: Campaign Object
        user: User object
        question: Question object
    Returns: Video Token string.
    """
    try:
        # TODO: if video answers become editable, beware of taking the last one out. Present solution can give a out of
        # range exception
        # s = Survey.objects.filter(user=user, question=question).order_by('-created_at')[0]
        s = Survey.objects.get(campaign=campaign, user=user, question=question)
    except ObjectDoesNotExist:
        s = None

    if s is not None and s.video_token is not None:
        return s.video_token

    return None


def adds_campaign_and_user_to_url(url, user_id, campaign_id):
    """
    Args:
        url: string
        user_id: int
        campaign_id: int
    Returns: string, url with get params.
    """
    params = {}
    if campaign_id:
        params['campaign_id'] = campaign_id
    if user_id:
        params['user_id'] = user_id
    return common.add_params_tu_url(url, params)


def get_right_button_action(question_number, user_id, campaign_id):
    """
    Gets the url of the next question, with params.
    Args:
        question_number: int, interview question number
        user_id: int or string
        campaign_id: int or string
    Returns: string, url with params
    """
    url = '{}'.format(question_number + 1)
    return adds_campaign_and_user_to_url(url, user_id, campaign_id)


def save_response(campaign, user, question_number, interview_obj, video_token):
    """
    Saves the response, from last question.
    Args:
        campaign: Campaign Object
        user: User object
        question_number: int, number interview question.
        interview_obj: Interview object
        video_token: string.
    Returns: None, saves Survey object.
    """
    if video_token is not None:
        try:
            previous_question = interview_obj.questions.get(order=question_number-1)
            Survey(campaign=campaign,
                   user=user,
                   question=previous_question,
                   interview=interview_obj,
                   video_token=video_token).save()
        except ObjectDoesNotExist:  # beyond last question
            pass  # cannot save, if the question is not found.


def get_top_message(on_interview):
    if on_interview:
        return _("Click on the video to hear the question")
    else:
        return _("Hi, I'm Santiago, Congratulations on passing the tests{test_score_str}!")


def get_message0(on_interview):
    if on_interview:
        return _("In 2 minutes:")
    else:
        return ''


def get_message1():
    return _("Hi, I'm Santiago, Congratulations on passing the tests{test_score_str}!")


def get_message2(enable_interview):
    if enable_interview:
        return _("Let's schedule an appointment or record your interview now!")
    else:
        return _("Let's schedule an appointment!")


def update_candidate_state(campaign, user, interview_obj, question_number):
    """
    If previous_question was the last question then it updates the candidate state to DIS (Did Interview in Standby)
    Args:
        campaign: obj
        user: obj
        interview_obj: Interview Object
        question_number: int
    Returns:
    """
    if question_number - 1 > 0:  # cannot ask for zero or negative questions
        previous_question = interview_obj.questions.get(order=question_number-1)
        if on_last_question(interview_obj, previous_question):
            try:
                candidate = Candidate.objects.get(user=user, campaign=campaign)
                candidate.state = State.objects.get(code='DIS')
                candidate.save()
            except ObjectDoesNotExist:  # the object hasn't been created yet, creates it.
                Candidate(campaign=campaign, user=user, state=State.objects.get(code='DIS')).save()
