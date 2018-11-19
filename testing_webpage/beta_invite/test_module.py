"""
Test related methods.
"""
from beta_invite import text_analizer
from beta_invite.models import Question, Survey, Score, Evaluation, EvaluationSummary, Test
from dashboard.models import Candidate, State
from match import model
import common


def get_tests_questions_dict(tests):
    """
    Args:
        tests: List of Test objects.
    Returns: {test_id: [question_id ...]}
    """
    return {test.id: [q.id for q in test.questions.all()] for test in tests}


def update_survey(question, answer_text, survey, question_id):
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
        survey.score = 0
        survey.save()
        return

    if question.type.code == 'SA':
        answer_id = int(answer_text)
        survey.answer_id = answer_id
        if answer_id in [q.id for q in Question.objects.get(pk=question_id).correct_answers.all()]:
            survey.score = 1
        else:
            survey.score = 0

    elif question.type.code == 'OF':
        survey.text_answer = answer_text
        survey.score = text_analizer.get_score(answer_text)

    elif question.type.code == 'MA':  # TODO: implement multiple answers.
        pass

    elif question.type.code == 'DOB':  # TODO: implement degree of belief.
        pass

    elif question.type.code == 'NI':
        if answer_text is None or answer_text == '':
            survey.score = 0
        else:
            number = int(answer_text.replace('.', '').replace(' ', ''))
            survey.numeric_answer = number
            if int(question.params['min_correct']) <= number <= int(question.params['max_correct']):
                survey.score = 1
            else:
                survey.score = 0

    survey.save()


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

    survey = Survey.create(campaign=campaign,
                           test_id=test_id,
                           question_id=question_id,
                           user_id=user_id)

    update_survey(question, answer_text, survey, question_id)

    candidate = Candidate.objects.get(campaign=campaign,
                                      user_id=user_id)

    candidate.surveys.add(survey)
    candidate.save()

    return survey.score


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
    for test_id, question_ids in questions_dict.items():

        test_score = get_test_score(campaign, question_ids, user_id, test_id, request)

        score = Score.create(test=Test.objects.get(pk=test_id),
                             value=test_score)
        score.save()

        scores.append(score)

    return scores


def automated_candidate_state_change(candidate, evaluation, use_machine_learning, success_state='WFI', fail_state='FT'):
    """
    Given tests results it alters the candidate state.
    :param candidate: Candidate
    :param evaluation: Evaluation
    :param use_machine_learning: Boolean indicating if ML is used
    :param success_state: if success will move to state.
    :param fail_state: if fail will move to state.
    :return: None
    """
    if candidate:

        # don't override human decisions
        if candidate.state in State.get_human_intervention_states():
            return

        if evaluation.passed:
            candidate.change_state(state_code=success_state,
                                   forecast=evaluation.passed,
                                   use_machine_learning=use_machine_learning)

        candidate.save()


def add_evaluation_to_candidate(candidate, evaluation):
    """
    Args:
        candidate: obj
        evaluation: obj
    Returns: Updates the candidate state if passes or not the test.
    """
    if candidate:
        candidate.evaluations.add(evaluation)
        candidate.evaluation_summary = EvaluationSummary.create(candidate.evaluations.all())
        candidate.save()


def get_evaluation(scores, candidate):
    """
    Args:
        scores: objects with current scores.
        candidate: obj
    Returns: get Evaluation object and links it ot user.
    """

    evaluation = Evaluation.create(scores=scores)
    update_scores(evaluation, scores)
    add_evaluation_to_candidate(candidate, evaluation)

    classify_evaluation_and_change_state(candidate)
    return evaluation


def get_candidate_from_evaluation(evaluation):
    return Candidate.objects.get(evaluations__contains=evaluation)


def average_list(my_list):
    """
    Average, if no elements outputs None
    :param my_list:
    :return:
    """
    my_list = [e for e in my_list if e is not None]
    if len(my_list) > 0:
        return sum(my_list) / len(my_list)
    else:
        return None


def passed_all_excluding_tests(self):
    return all([s.passed for s in self.scores.filter(test__excluding=True)])


def passed_all_excluding_questions(evaluation, candidate):

    for score in evaluation.scores.all():
        excluding_questions = score.test.questions.filter(excluding=True)

        for question in excluding_questions:
            survey = Survey.get_last_try(candidate.campaign,
                                         score.test,
                                         question,
                                         candidate.user)
            if survey and survey.score == 0:  # Failed Question
                return False

    return True


def update_scores(evaluation, scores):

    evaluation.scores = scores

    if evaluation.scores:

        evaluation.cut_score = average_list([s.test.cut_score for s in evaluation.scores.all()])
        evaluation.final_score = average_list([s.value for s in evaluation.scores.all()])

        evaluation.cognitive_score = evaluation.get_score_for_test_type('cognitive')
        evaluation.technical_score = evaluation.get_score_for_test_type('technical')
        evaluation.requirements_score = evaluation.get_score_for_test_type('requirements')
        evaluation.motivation_score = evaluation.get_score_for_test_type('motivation')
        evaluation.cultural_fit_score = evaluation.get_score_for_test_type('cultural fit')
        # TODO: add any new score here

    evaluation.save()


def classify_evaluation_and_change_state(candidate, use_machine_learning=False, success_state='WFI', fail_state='FT'):
    """
    does the ML and changes candidate state
    :param candidate: given a candidate last saved state. Classifies
    :param use_machine_learning: if True will use machine learning algorithm, else will use simple heuristic
    :param success_state: State if success
    :param fail_state: State if fails
    :return: None or raises Error
    """
    last_evaluation = candidate.get_last_evaluation()

    if last_evaluation is not None:

        forecast = model.get_candidate_match_and_save(candidate) if use_machine_learning else last_evaluation.final_score >= last_evaluation.cut_score

        last_evaluation.passed = forecast and \
            passed_all_excluding_tests(last_evaluation) and \
            passed_all_excluding_questions(last_evaluation, candidate)
        last_evaluation.save()

        automated_candidate_state_change(candidate, last_evaluation,
                                         use_machine_learning=use_machine_learning,
                                         success_state=success_state,
                                         fail_state=fail_state)

    else:
        raise NotImplementedError('should not reach this, something wrong with candidate_id: {}'.format(candidate.id))


def get_score(scores, test_id):
    result = [s for s in scores if s.test_id == test_id]
    if len(result) == 1:
        return result[0]
    else:
        return None


def update_scores_of_candidate(candidate):
    """
    Updates the user.scores according to a candidate
    :param candidate: Candidate
    :return: None
    """

    scores = list(candidate.user.scores.all())

    last_evaluation = candidate.get_last_evaluation()
    if last_evaluation:
        for last_score in last_evaluation.scores.all():
            another_score = get_score(scores, last_score.test_id)

            if another_score:  # already has the test
                if another_score.created_at < last_score.created_at:  # has a more recent test
                    common.replace(scores, another_score, last_score)
            else:  # does not have the test
                scores.append(last_score)

        candidate.user.scores = scores
        candidate.user.save()


def update_scores_of_user(user):
    """
    Will update scores according to all its candidates
    :param user: just a User
    :return: None
    """

    candidates = common.get_candidates(user)
    for c in candidates:
        update_scores_of_candidate(c)


def get_high_scores(candidate):
    """
    Will get scores higher than average between 100 and cut_score
    :param candidate:
    :return:
    """
    all_tests = list(candidate.campaign.tests.all())
    high_scores = candidate.user.scores.filter(test__in=all_tests, passed=True).all()
    return [s for s in high_scores if s.value > (100 + s.test.cut_score)/2]


def get_missing_tests(candidate):
    """
    Gets the tests that the user should present either because:
    1. He/she has never presented it
    2. Failed the test, the last time he/she presented it
    3. Passed with a low score

    high_score = above the average between test.cut_score and 100
    :param candidate: Candidate object
    :return: list of tests
    """
    all_tests = list(candidate.campaign.tests.all())
    high_score_tests = [s.test for s in get_high_scores(candidate)]

    # filters for low or non existent tests
    tests = [t for t in all_tests if t not in high_score_tests]

    # sorts by test_type.order
    return sorted(tests, key=lambda t: t.type.order)

