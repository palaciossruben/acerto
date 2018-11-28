"""
Test related methods.
"""
import re
from django.db.models import F
import wave
import os
import audioop

from beta_invite import text_analizer
from beta_invite.models import Question, Survey, Score, Evaluation, EvaluationSummary, Test
from dashboard.models import Candidate, State
from match import model
import common
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def get_tests_questions_dict(tests):
    """
    Args:
        tests: List of Test objects.
    Returns: {test_id: [question_id ...]}
    """
    return {test.id: [q for q in test.questions.all()] for test in tests}


def get_cosine_similarity(*strings):
    """
    see: https://towardsdatascience.com/overview-of-text-similarity-metrics-3397c4601f50
    :param strings:
    :return:
    """
    vectors = [t for t in get_vectors(*strings)]
    similarity = cosine_similarity(vectors)
    return similarity[0][1]


def get_vectors(*strings):
    text = [t.lower() for t in strings]
    vectorizer = CountVectorizer(text)
    vectorizer.fit(text)
    return vectorizer.transform(text).toarray()


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
    elif question.type.code == 'R':
        """
        Compares similarities between detected text and real text
        """
        survey.text_answer = answer_text

        # TODO: add English
        question_text = question.text_es

        # takes the inside of double quotes
        matches = re.findall(r'\".+\"', question_text)
        if len(matches) > 0 and len(matches[-1]) > 2:
            original_text = matches[-1][1:-1]
            survey.score = get_cosine_similarity(answer_text, original_text)
        else:
            survey.score = 0  # THIS IS A TEST FAILURE
    else:
        raise NotImplementedError('question type not implemented')

    survey.save()


def add_survey_to_candidate(campaign, test_id, question, user_id, answer_text):
    survey = Survey.create(campaign=campaign,
                           test_id=test_id,
                           question_id=question.id,
                           user_id=user_id)

    update_survey(question, answer_text, survey, question.id)

    candidate = Candidate.objects.get(campaign=campaign,
                                      user_id=user_id)

    candidate.surveys.add(survey)
    candidate.save()
    return survey


def process_question_and_get_score(campaign, question, request, test_id, user_id):
    """
    Args:
        campaign: Campaign Object
        question: Question
        request: HTTP
        test_id: int
        user_id: int
    Returns: creates a Survey object and gets the score.
    """
    answer_text = request.POST.get('test_{}_question_{}'.format(test_id, question.id))

    if question.type.code == 'R':  # In this case the solution should be ready by transcribing!
        survey = Survey.objects.filter(campaign=campaign,
                                       test_id=test_id,
                                       question_id=question.id,
                                       user_id=user_id).order_by('-created_at').first()
    else:
        survey = add_survey_to_candidate(campaign, test_id, question, user_id, answer_text)

    if survey is not None:
        return survey.score
    else:
        return 0


def get_test_score(campaign, questions, user_id, test_id, request):
    """
    Args:
        campaign: Campaign Object
        questions: collection of questions
        user_id: int
        test_id: int
        request: HTTP
    Returns: The score, a percentage (result/score), handling division by zero.
    """
    total = 0
    result = 0

    for question in questions:
        total += 1
        result += process_question_and_get_score(campaign, question, request, test_id, user_id)

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
    for test_id, questions in questions_dict.items():
        test_score = get_test_score(campaign, questions, user_id, test_id, request)
        score = Score.create(test=Test.objects.get(pk=test_id), value=test_score)
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

        else:
            candidate.change_state(state_code=fail_state,
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
                    scores = common.replace(scores, another_score, last_score)
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

    # TODO: optimize this code:
    all_tests = list(candidate.campaign.tests.all())
    high_scores = candidate.user.scores.filter(test__in=all_tests,  # F('candidate__campaign__tests'),
                                               value__gt=(100 + F('test__cut_score'))/2,
                                               passed=True).all()
    return list(high_scores)


def get_missing_tests(candidate, high_scores=None):
    """
    Gets the tests that the user should present either because:
    1. He/she has never presented it
    2. Failed the test, the last time he/she presented it
    3. Passed with a low score

    high_score = above the average between test.cut_score and 100
    :param candidate: Candidate object
    :param high_scores: can have this param to save time calculating it
    :return: list of tests
    """
    all_tests = list(candidate.campaign.tests.all())

    if high_scores is None:
        high_scores = get_high_scores(candidate)
    high_score_tests = [s.test for s in high_scores]

    # filters for low or non existent tests
    tests = [t for t in all_tests if t not in high_score_tests]

    # sorts by test_type.order
    return sorted(tests, key=lambda t: t.type.order)


def down_sample_wave(src, dst, inrate=44100, outrate=16000, inchannels=2, outchannels=1):
    if not os.path.exists(src):
        print('Source not found!')
        return False

    if not os.path.exists(os.path.dirname(dst)):
        os.makedirs(os.path.dirname(dst))

    try:
        s_read = wave.open(src, 'r')
        s_write = wave.open(dst, 'w')
    except FileNotFoundError:
        print('Failed to open files!')
        return False

    n_frames = s_read.getnframes()
    data = s_read.readframes(n_frames)

    #try:
    converted = audioop.ratecv(data, 2, inchannels, inrate, outrate, None)
    if outchannels == 1:
        converted = audioop.tomono(converted[0], 2, 1, 0)
    #except:
    #    print('Failed to downsample wav')
    #    return False

    try:
        s_write.setparams((outchannels, 2, outrate, 0, 'NONE', 'Uncompressed'))
        s_write.writeframes(converted)
    except:
        print('Failed to write wav')
        return False

    s_read.close()
    s_write.close()

    return True



# TODO: remove?
import wave
import numpy as np
import scipy.signal as sps


class DownSample:
    def __init__(self, in_rate, out_rate):
        self.in_rate = in_rate
        self.out_rate = out_rate

    def open_file(self, fname):
        try:
            self.in_wav = wave.open(fname)
        except:
            print("Cannot open wav file (%s)" % fname)
            return False

        if self.in_wav.getframerate() != self.in_rate:
            print("Frame rate is not %d (it's %d)" % \
                  (self.in_rate, self.in_wav.getframerate()))
            return False

        self.in_nframes = self.in_wav.getnframes()
        print("Frames: %d" % self.in_wav.getnframes())

        if self.in_wav.getsampwidth() == 1:
            self.nptype = np.uint8
        elif self.in_wav.getsampwidth() == 2:
            self.nptype = np.uint16

        return True

    def resample(self, fname):
        self.out_wav = wave.open(fname, "w")
        self.out_wav.setframerate(self.out_rate)
        self.out_wav.setnchannels(self.in_wav.getnchannels())
        self.out_wav.setsampwidth (self.in_wav.getsampwidth())
        self.out_wav.setnframes(1)

        print("Nr output channels: %d" % self.out_wav.getnchannels())

        audio = self.in_wav.readframes(self.in_nframes)
        nroutsamples = round(len(audio) * self.out_rate/self.in_rate)
        print("Nr output samples: %d" %  nroutsamples)

        audio_out = sps.resample(np.fromstring(audio, self.nptype), nroutsamples)
        audio_out = audio_out.astype(self.nptype)

        self.out_wav.writeframes(audio_out.copy(order='C'))

        self.out_wav.close()
