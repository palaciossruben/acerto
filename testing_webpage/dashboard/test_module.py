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

                if 'type' in key:
                    setattr(question, 'type_id', value)

                elif re.match(r'.*question_text$', key):
                    setattr(question, 'text', value)

                elif re.match(r'.*question_text_es$', key):
                    setattr(question, 'text_es', value)

                elif 'image' in key:
                    file_path = common.save_resource_from_request(request=request,
                                                                  my_object=question,
                                                                  param_name='image_path',
                                                                  folder_name='questions')
                    setattr(question, 'image_path', file_path)

                question.save()

    test.questions = list(question_set)
    return test
