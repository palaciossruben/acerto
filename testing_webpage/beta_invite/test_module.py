"""
Test related methods.
"""
import common
from beta_invite import text_analizer
from beta_invite.models import Question, Survey, Score, Test, Evaluation, User
from dashboard.models import Candidate, State


def average_list(array):
    return sum(array)/len(array)


def get_tests_questions_dict(tests):
    """
    Args:
        tests: List of Test objects.
    Returns: {test_id: [question_id ...]}
    """
    return {test.id: [q.id for q in test.questions.all()] for test in tests}


def get_score_and_updates_survey(question, answer_text, survey, question_id):
    """
    Manages the logic for different kinds of questions. And for each question decides to give points to result or not.
    Args:
        question: Question object
        answer_text: string
        survey: Survey object
        question_id: int
    Returns: updates result and survey Object
    """
    if answer_text is None:
        return 0

    if question.type.code == 'SA':
        answer_id = int(answer_text)
        survey.answer_id = answer_id
        if answer_id in [q.id for q in Question.objects.get(pk=question_id).correct_answers.all()]:
            return 1

    elif question.type.code == 'OF':
        survey.text_answer = answer_text
        return text_analizer.get_score(answer_text)

    elif question.type.code == 'MA':  # TODO: implement multiple answers.
        pass

    elif question.type.code == 'DOB':  # TODO: implement degree of belief.
        pass

    elif question.type.code == 'NI':
        number = int(answer_text)
        survey.numeric_answer = number
        if question.params['min_correct'] <= number <= question.params['max_correct']:
            return 1

    return 0  # failed the question.


def process_question_and_get_score(campaign, question_id, request, test_id, user_id):
    """
    Args:
        campaign: Campaign Object
        question_id: int
        request: HTTP
        test_id: int
        user_id: int
    Returns: creates a Survey object and gets the score.
    """
    question = Question.objects.get(pk=question_id)
    answer_text = request.POST.get('test_{}_question_{}'.format(test_id, question_id))

    survey = Survey(campaign=campaign,
                    test_id=test_id,
                    question_id=question_id)

    if user_id:
        survey.user_id = int(user_id)

    score = get_score_and_updates_survey(question, answer_text, survey, question_id)

    survey.save()

    return score


def get_test_score(campaign, question_ids, user_id, test_id, request):
    """
    Args:
        campaign: Campaign Object
        question_ids: collection of question ids
        user_id: int
        test_id: int
        request: HTTP
    Returns: The score, a percentage (result/score), handling division by zero.
    """
    total = 0
    result = 0

    for question_id in question_ids:
        total += 1
        result += process_question_and_get_score(campaign, question_id, request, test_id, user_id)

    return text_analizer.handle_division_by_zero(result, total)*100


def get_scores(campaign, user_id, questions_dict, request):
    """
    Args:
        campaign: Campaign Object
        user_id: int
        questions_dict: {test_id: [question_id ...]}
        request: HTTP
    Returns: tuple: cut_scores, scores
    """
    scores = []
    cut_scores = []
    for test_id, question_ids in questions_dict.items():
        cut_scores.append(Test.objects.get(pk=test_id).cut_score)

        test_score = get_test_score(campaign, question_ids, user_id, test_id, request)

        score = Score(test_id=test_id,
                      value=test_score)
        if user_id:
            score.user_id = int(user_id)
        score.save()

        scores.append(test_score)

    return cut_scores, scores


def update_candidate_state(campaign, user_id, evaluation):
    """
    Args:
        campaign: obj
        user_id: int
        evaluation: obj
    Returns: Updates the candidate state if passes or not the test.
    """
    if user_id:

        candidate = Candidate.objects.get(campaign=campaign, user_id=user_id)
        candidate.evaluations.add(evaluation)

        if evaluation.passed:
            candidate.state = State.objects.get(code='WFI')
            candidate.save()
        else:  # Fails tests
            candidate.state = State.objects.get(code='WFT')
            candidate.save()


def get_evaluation(cut_scores, scores, campaign, user_id):
    """
    simple average and percentage
    Args:
        cut_scores: list of passing scores.
        scores: current scores.
        campaign: object
        user_id: int
    Returns: get Evaluation object and links it ot user.
    """
    cut_score = average_list(cut_scores)
    final_score = average_list(scores)

    evaluation = Evaluation(campaign=campaign,
                            cut_score=cut_score,
                            final_score=final_score)

    evaluation.save()

    update_candidate_state(campaign, user_id, evaluation)

    return evaluation


def comes_from_test(request):
    """
    Args:
        request: HTTP
    Returns: Boolean, indicating if the last url was the test. If no refrer url present then it will return false
    """
    return '/post' in common.remove_params_from_url(request.META.get('HTTP_REFERER', ''))
