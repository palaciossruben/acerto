import re

import common
from beta_invite.models import Question, Answer
from django.core.exceptions import ObjectDoesNotExist


def get_question(question_answer_dict, test, key):

    try:
        question_order = int(re.findall('^\d+', key)[0])
    except IndexError:
        return None  # no valid question id found

    if question_order not in [q.order for q in question_answer_dict.keys()]:

        # Try finding question first, if not then create
        try:
            question = Question.objects.get(pk__in={q.pk for q in test.questions.all()}, order=question_order)
        except ObjectDoesNotExist:  # new question.
            question = Question(order=question_order)
            question.save()
    else:
        question = [q for q in question_answer_dict.keys() if q.order == question_order][0]

    return question


def get_answer(question_answer_dict, question, key):

    try:
        answer_order = int(re.findall('^\d+', key)[0])
    except IndexError:
        return None  # no valid answer id found

    if answer_order not in [a.order for a in question_answer_dict[question]]:  # Add missing answer

        # Try finding question first, if not then create
        try:
            answer = Answer.objects.get(pk__in={a.pk for a in question.answers.all()}, order=answer_order)
        except ObjectDoesNotExist:  # new answer.
            answer = Answer(order=answer_order)
            answer.save()
    else:
        answer = [a for a in question_answer_dict[question] if a.order == answer_order][0]

    return answer


def update_test_questions(test, request):
    """
    Args:
        test: Test Object
        request: HTTP request
    Returns: None, updates or creates new questions.
    """

    # TODO: shittiest code ever! REFACTOR

    question_answer_dict = dict()  # dictionary with key=question value={answers}
    correct_answers_dict = dict()  # dictionary with key=question value={correct_answers}

    for key, value in request.POST.items():

        # When there is an attribute with a a question and its not the image
        if 'question' in key and 'image_path' not in key:

            question = get_question(question_answer_dict, test, key)

            if question:

                # init dicts.
                if question_answer_dict.get(question) is None:
                    question_answer_dict[question] = set()

                if correct_answers_dict.get(question) is None:
                    correct_answers_dict[question] = set()

                question_attribute_name = common.get_object_attribute_name(key, question)
                if question_attribute_name in question.__class__.__dict__:  # Attribute is part of the class
                    setattr(question, question_attribute_name, value)
                else:  # if not, it might be an answer

                    answer_attribute_name = common.get_object_attribute_name(question_attribute_name, Answer)
                    answer = get_answer(question_answer_dict, question, question_attribute_name)

                    if answer:
                        question_answer_dict[question].add(answer)

                    if answer_attribute_name in answer.__class__.__dict__:  # Attribute is part of the class

                        setattr(answer, answer_attribute_name, value)
                        answer.save()

                    elif 'is_correct' in answer_attribute_name and value == 'on':
                        correct_answers_dict[question].add(answer)
                    else:  # its not part of answers, then it will go into the question params.

                        # TODO: this is shitty code, assumes all params are ints.
                        if question.params:
                            question.params[question_attribute_name] = int(value)
                        else:
                            question.params = {question_attribute_name: int(value)}

                question.remove_answer_gaps()
                question.save()

    # determine all answers to questions:
    for q, answers in question_answer_dict.items():
        q.answers = answers
        q.save()

    # determine correct answers to questions:
    for q, correct_answers in correct_answers_dict.items():
        q.correct_answers = correct_answers
        q.save()

    test.questions = question_answer_dict.keys()

    # save attachments
    for question in question_answer_dict.keys():
        image_path = common.save_resource_from_request(request=request,
                                                       my_object=question,
                                                       param_name='{}_question_image_path'.format(question.order),
                                                       folder_name='questions')

        if image_path != '#':
            setattr(question, 'image_path', image_path)
            question.save()

    test.remove_question_gaps()

    return test
