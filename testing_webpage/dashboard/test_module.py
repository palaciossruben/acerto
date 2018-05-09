import re

import common
from beta_invite.models import Question, Answer
from django.core.exceptions import ObjectDoesNotExist


def get_question(question_set, test, key):

    try:
        question_order = int(re.findall('^\d+', key)[0])
    except IndexError:
        return None  # no valid question id found

    if question_order not in [q.order for q in question_set]:

        # Try finding question first, if not then create
        try:
            question = Question.objects.get(pk__in={q.pk for q in test.questions.all()}, order=question_order)
        except ObjectDoesNotExist:  # new question.
            question = Question(order=question_order)
            question.save()
    else:
        question = [q for q in question_set if q.order == question_order][0]

    return question


def get_answer(answer_set, question, key):

    try:
        answer_order = int(re.findall('^\d+', key)[0])
    except IndexError:
        return None  # no valid answer id found

    if answer_order not in [a.order for a in answer_set]:  # Create missing question

        # Try finding answer first, if not then create one
        #try:
        #    answer = Answer.objects.get(pk__in={a.pk for a in question.answers.all()}, order=answer_order)
        #except ObjectDoesNotExist:
            # Create missing answer
        #    answer = Answer(order=answer_order)
        #    answer.save()

        # TODO: remove temp solution to solve the order=None issue.
        # Sorts answers on backend and template by pk
        answers = [a for a in question.answers.all()]
        index = answer_order - 1
        if len(answers) > index:
            answer = answers[index]  # correct for 0 indexing
        else:  # new answer
            answer = Answer(order=answer_order)
            answer.save()
            question.answers.add(answer)
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
    correct_answers_dict = dict()

    for key, value in request.POST.items():

        # When there is an attribute with a a question.
        if 'question' in key:

            question = get_question(question_set, test, key)

            if question:
                question_set.add(question)

                if correct_answers_dict.get(question, None) is None:
                    correct_answers_dict[question] = set()

                question_attribute_name = common.get_object_attribute_name(key, question)
                if question_attribute_name in question.__class__.__dict__:  # Attribute is part of the class

                    if 'image_path' in key:
                        value = common.save_resource_from_request(request=request,
                                                                  my_object=question,
                                                                  param_name='image_path',
                                                                  folder_name='questions')
                    setattr(question, question_attribute_name, value)
                else:  # if not it might be an answer

                    answer_attribute_name = common.get_object_attribute_name(question_attribute_name, Answer)
                    answer = get_answer(answer_set, question, question_attribute_name)

                    if answer_attribute_name in answer.__class__.__dict__:  # Attribute is part of the class

                        setattr(answer, answer_attribute_name, value)
                        answer.save()
                        answer_set.add(answer)

                    elif 'is_correct' in answer_attribute_name and value == 'correct':
                        correct_answers_dict[question].add(answer)

                    if answer not in question.answers.all():
                        question.answers.add(answer)

                question.save()

                if question not in test.questions.all():
                    test.questions.add(question)

    # determine correct values:
    for q, correct_answers in correct_answers_dict.items():
        q.correct_answers = correct_answers
        q.save()

    return test
