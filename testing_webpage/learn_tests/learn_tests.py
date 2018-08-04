"""
Learns the importance of each question separating the candidates
"""
import os
import sys

from django.core.wsgi import get_wsgi_application

# Environment can use the models as if inside the Django app
sys.path.insert(0, '/'.join(os.getcwd().split('/')[:-1]))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

import statistics
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import confusion_matrix
from imblearn.over_sampling import ADASYN

import common
from dashboard.models import State
from beta_invite.models import Test, Survey
from match import learn


NUMBER_OF_TRIALS = 20


def new_balance(data):
    """
    Balances samples with ADASYN algorithm:
    http://sci2s.ugr.es/keel/pdf/algorithm/congreso/2008-He-ieee.pdf
    :param data: the dataframe
    :return: dataframe
    """

    print('unbalanced positive weight: ' + str(np.mean(data.target)))

    # Apply the random over-sampling
    ada = ADASYN()
    try:
        features, target = ada.fit_sample(data.features, data.target)
    except ValueError:  # ValueError: No samples will be generated with the provided ratio settings.
        return None

    print('balanced positive weight: ' + str(np.mean(target)))

    new_df = pd.DataFrame(features, columns=list(data.features))
                                    #index=data.features.index.values)

    return learn.DataPair(features=new_df, target=list(target))


def get_questions_and_candidates(test):

    surveys = Survey.objects.filter(test=test)
    questions = test.questions.all()

    candidates = dict()
    for survey in surveys:

        if survey.score is not None and survey.test.cut_score:
            candidate = common.get_candidate(survey.user, survey.campaign)

            if candidate:
                passed = 1 if survey.score > survey.test.cut_score/100 else 0

                if candidates.get(candidate) is None:
                    candidates[candidate] = dict()

                candidates[candidate][survey.question] = passed

    return questions, candidates


def update_importance(test):
    questions, candidates = get_questions_and_candidates(test)
    df = pd.DataFrame(columns=[q.id for q in questions] + ['passed'],
                      index=[c.id for c in candidates.keys()])

    # only process worthwhile tests
    if len(candidates) < 20:
        return

    try:
        print('processing test: {}'.format(test))
    except:
        pass
    print('processing test: {}'.format(test).encode('utf-8'))

    #total_trivial = 0
    #right_trivial = 0
    for candidate, values in candidates.items():

        if candidate.state in State.get_rejected_states() + State.get_recommended_states():
            end_state_passes = 1 if candidate.state in State.get_recommended_states() else 0
            df.loc[candidate.id, 'passed'] = end_state_passes
            #print(test.cut_score/100)
            #print(int(sum(values.values())))
            #print(test.cut_score/100 * len(questions))
            trivial_rule = int(sum(values.values()) >= test.cut_score/100 * len(questions))

            #total_trivial += 1
            #right_trivial += trivial_rule == end_state_passes

            for question, passed in values.items():
                df.loc[candidate.id, question.id] = passed

    df.dropna(axis=0, inplace=True)

    data = learn.DataPair(target=df['passed'])
    df.drop('passed', axis=1, inplace=True)
    data.features = df

    data = new_balance(data)
    if data is None:  # could'nt do the re-balance will exit.
        return

    # TODO: measure trivial solution after rebalancing
    """
    total_trivial = 0
    right_trivial = 0
    for candidate, values in candidates.items():

        if candidate.state in State.get_rejected_states() + State.get_recommended_states():
            end_state_passes = 1 if candidate.state in State.get_recommended_states() else 0
            trivial_rule = int(sum(values.values()) > test.cut_score * len(questions))

            total_trivial += 1
            right_trivial += trivial_rule == end_state_passes
    """

    importance = pd.DataFrame(columns=list(df))
    cross_val_scores_array = []
    for seed in range(NUMBER_OF_TRIALS):

        X_train, X_test, y_train, y_test = train_test_split(data.features, list(data.target),
                                                            test_size=0.3,
                                                            random_state=seed)

        parameters = {'max_depth': (2, 4, 8, 16), 'n_estimators': [5, 10, 20, 40, 80]}

        grid_model = GridSearchCV(RandomForestClassifier(), parameters, n_jobs=1)
        grid_model.fit(X_train, y_train)

        print('optimal params: ' + str(grid_model.best_params_))

        model = RandomForestClassifier(max_depth=grid_model.best_params_['max_depth'],
                                       n_estimators=grid_model.best_params_['n_estimators'])
        model.fit(X_train, y_train)

        c = statistics.mean([float(e) for e in cross_val_score(model, X_test, y_test, scoring='accuracy')])
        cross_val_scores_array.append(c)

        p = model.feature_importances_
        importance = importance.append({col: value for col, value in zip(list(df), p)}, ignore_index=True)

    mean_importance = importance.mean()
    for q in questions:
        q.importance = mean_importance.loc[q.id]
        q.save()

    print('importance avg: ' + str(mean_importance))
    print('importance std: ' + str(importance.std()))

    print('Confusion Matrix:')
    test_prediction = model.predict(X_test)
    print(confusion_matrix(y_test, test_prediction))

    # TODO: missing trivial
    #trivial_accuracy = right_trivial / total_trivial
    #print('trivial accuracy: ' + str(trivial_accuracy))
    print('trivial accuracy: TODO')

    cross_val = statistics.mean(cross_val_scores_array)
    #print('delta (cross_val - trivial): ' + str(cross_val - trivial_accuracy))
    print('delta (cross_val - trivial): TODO')
    print('avg cross val: ' + str(cross_val))
    print('std cross val: ' + str(statistics.stdev(cross_val_scores_array)))


if __name__ == '__main__':
    for test in Test.objects.all():
        #if 'Basic Accounting Test' in test.name:
        update_importance(test)
