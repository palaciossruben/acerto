import re
from beta_invite.models import Question


def update_question_attr(test, dict_id, key_question_dict, value, attribute_name):
    """
    Uses meta-programing, and updates or creates new Question objects.
    Args:
        test: Object
        dict_id: temporal id to distinguish between different new ids only.
        key_question_dict: dictionary containing new stored questions to add.
        value:
        attribute_name: the name of the Bullet object attribute.
    Returns: None, just update
    """
    if dict_id in key_question_dict.keys():  # Updates question.
        q = key_question_dict[dict_id]
        setattr(q, attribute_name, value)
        q.save()
    else:  # creates new Question
        q = Question(**{attribute_name: value})
        q.save()
        key_question_dict[dict_id] = q
        test.questions.add(q)


def update_test_questions(test, request):
    """
    Args:
        test: Test Object
        request: HTTP request
    Returns: None, updates or creates new questions.
    """
    key_question_dict = {}
    for key, value in request.POST.items():

        # When there is a new_question.
        if 'new_question' in key:

            dict_id = int(re.findall('^\d+', key)[0])

            if 'type' in key:
                update_question_attr(test, dict_id, key_question_dict, value, 'question_type_id')

            elif re.match(r'.*question_name$', key):
                update_question_attr(test, dict_id, key_question_dict, value, 'name')

            elif re.match(r'.*question_name_es$', key):
                update_question_attr(test, dict_id, key_question_dict, value, 'name_es')

        # updates existing questions
        elif re.search('\d+_question', key):

            # gets the question id.
            question_pk = int(re.findall(r'\d+', key)[0])
            question = Question.objects.get(pk=question_pk)

            if 'type' in key:
                question.question_type_id = value

            elif re.match(r'.*question_name$', key):
                question.name = value

            elif re.match(r'.*question_name_es$', key):
                question.name_es = value

            question.save()

    test.save()
