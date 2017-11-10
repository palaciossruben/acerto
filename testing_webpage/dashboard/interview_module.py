"""
Helper functions related to the dashboard and interviews.
"""

from beta_invite.models import Question


def get_new_question(new_question_text, new_question_text_es, video_token):
    """
    Args:
        new_question_text: question statement
        new_question_text_es: question statement in Spanish
        video_token: string with video id
    Returns: Question object or None.
    """

    if video_token is not None:
        # By the model, the Question is be default the first one. (order=1)
        question = Question(text=new_question_text,
                            text_es=new_question_text_es,
                            video_token=video_token)
        question.save()
        return question
    else:
        return None


def assign_order_to_question(new_question, interview_obj):
    """
    The new question is always the last question.
    Args:
        new_question: Question Object
        interview_obj: Interview Object
    Returns: Updates the Question object.
    """
    new_question.order = len({q for q in interview_obj.questions.all()}) + 1
    new_question.save()


def update_old_question_statements(request, interview_obj, new_question):
    """
    Args:
        request: HTTP object
        interview_obj: Interview object
        new_question: The object just created.
    Returns: None, just updates the objects.
    """

    # Removes the new_question if it is not None.
    if new_question is not None:
        old_questions = interview_obj.questions.exclude(id=new_question.id).all()
    else:
        old_questions = interview_obj.questions.all()

    for q in old_questions:

        text = request.POST.get('{}_text'.format(q.video_token))
        text_es = request.POST.get('{}_text_es'.format(q.video_token))

        # Never have Nones floating around but empty spaces for placeholders to work on the frontend.
        q.text = '' if text is None else text
        q.text_es = '' if text_es is None else text_es

        q.save()
