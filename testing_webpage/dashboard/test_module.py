import re

import common
from beta_invite.models import Question


def get_question(question_set, key):

    try:
        question_order = int(re.findall('^\d+', key)[0])
    except IndexError:
        return None  # no valid question id found

    if question_order not in [q.order for q in question_set]:  # Create missing question
        question = Question(order=question_order)
        question.save()
    else:
        question = [q for q in question_set if q.order == question_order][0]

    return question


def update_test_questions(test, request):
    """
    Args:
        test: Test Object
        request: HTTP request
    Returns: None, updates or creates new questions.
    """
    question_set = set()
    for key, value in request.POST.items():

        # When there is a new_question.
        if 'question' in key:

            question = get_question(question_set, key)

            if question:
                question_set.add(question)

                if 'image_path' in key:
                    value = common.save_resource_from_request(request=request,
                                                              my_object=question,
                                                              param_name='image_path',
                                                              folder_name='questions')

                setattr(question, common.get_object_attribute_name(key, question), value)

                question.save()

    test.questions = list(question_set)
    return test
