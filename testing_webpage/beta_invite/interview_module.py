"""
This is a helper module for the interview.
"""


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


