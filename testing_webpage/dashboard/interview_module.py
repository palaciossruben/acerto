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


def update_text(question, new_text, attribute_name):
    """
    Args:
        question: Object
        new_text: string or None
        attribute_name: the name of the text field to update on the Question object.
    Returns: updates question text
    """
    question_text = getattr(question, attribute_name)

    # Never have Nones floating around but empty spaces for placeholders to work on the frontend.
    if question_text is None and new_text is None:
        setattr(question, attribute_name, '')

    if new_text is not None:
        setattr(question, attribute_name, new_text)

    question.save()


def get_question(request):
    """
    Args:
        request: HTTP
    Returns: Question object
    """
    question_id = int(request.POST.get('question_id'))
    return Question.objects.get(pk=question_id)


def get_sorted_tuples(surveys):
    """
    Args:
        surveys: Survey Objects.
    Returns: (Question, Survey) tuples. Sorted by Question.order
    """
    question_answer_tuples = zip([s.question for s in surveys], surveys)
    return sorted(question_answer_tuples, key=lambda my_tuple: my_tuple[0].order)


def create_question(request, campaign):
    """
    Given a new_token_id and texts, it creates a new question.
    Args:
        request: HTTP
        campaign: Campaign Object
    Returns: None, Adds a new video.
    """

    new_video_token = request.POST.get('new_video_token')
    new_question_text = request.POST.get('new_question_text')
    new_question_text_es = request.POST.get('new_question_text_es')

    new_question = get_new_question(new_question_text, new_question_text_es, new_video_token)

    # TODO: change this when a campaign has more than 1 interview.
    interview_obj = campaign.interviews.all()[0]
    if new_question is not None:
        assign_order_to_question(new_question, interview_obj)
        interview_obj.questions.add(new_question)
        interview_obj.save()


def update_question(request):
    """
    Args:
        request: HTTP object
    Returns: None, just updates the objects.
    """

    question = get_question(request)

    text = request.POST.get('text')
    text_es = request.POST.get('text_es')

    update_text(question, text, 'text')
    update_text(question, text_es, 'text_es')


def delete_question(request, campaign):
    """
    Args:
        request: HTTP object
        campaign: Campaign object
    Returns: None, just removes a question.
    """

    question = get_question(request)
    interview_obj = campaign.interviews.all()[0]
    interview_obj.questions.remove(question)
    interview_obj.save()

