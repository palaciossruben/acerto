import re

import common
from beta_invite.models import Question, Answer


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


def get_answer(answer_set, key):

    try:
        answer_order = int(re.findall('^\d+', key)[0])
    except IndexError:
        return None  # no valid answer id found

    if answer_order not in [a.order for a in answer_set]:  # Create missing question
        answer = Answer()
        answer.save()
    else:
        answer = [a for a in answer_set if a.order == answer_order][0]

    return answer


def update_test_questions(test, request):
    """
    Args:
        test: Test Object
        request: HTTP request
    Returns: None, updates or creates new questions.
    """
    question_set = set()
    answer_set = set()
    for key, value in request.POST.items():

        # When there is a new_question.
        if 'question' in key:

            question = get_question(question_set, key)

            if question:
                question_set.add(question)

                question_attribute_name = common.get_object_attribute_name(key, question)
                if question_attribute_name in question.__class__.__dict__:  # Attribute is part of the class

                    if 'image_path' in key:
                        value = common.save_resource_from_request(request=request,
                                                                  my_object=question,
                                                                  param_name='image_path',
                                                                  folder_name='questions')
                    setattr(question, question_attribute_name, value)
                else:  # if not it might be an answer
                    answer = Answer()
                    answer_attribute_name = common.get_object_attribute_name(question_attribute_name, Answer)
                    setattr(answer, answer_attribute_name, value)


                question.save()

    test.questions = list(question_set)
    return test
