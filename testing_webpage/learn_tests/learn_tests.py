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
from beta_invite.models import Test, Survey, Question
from match import learn


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
        pass

    print('balanced positive weight: ' + str(np.mean(target)))

    new_df = pd.DataFrame(features, columns=list(data.features))
                                    #index=data.features.index.values)

    return learn.DataPair(features=new_df, target=list(target))


def get_questions_and_candidates():

    cognitive_test = Test.objects.get(name='Cognitive Test')
    surveys = Survey.objects.filter(test=cognitive_test)
    questions = cognitive_test.questions.all()

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


questions, candidates = get_questions_and_candidates()

df = pd.DataFrame(columns=[q.id for q in questions] + ['passed'],
                  index=[c.id for c in candidates.keys()])


total_base = 0
right_base = 0
for candidate, values in candidates.items():

    if candidate.state in State.get_rejected_states() + State.get_recommended_states():
        end_state_passes = 1 if candidate.state in State.get_recommended_states() else 0
        df.loc[candidate.id, 'passed'] = end_state_passes
        trivial_rule = int(sum(values.values()) > 4)

        total_base += 1
        right_base += trivial_rule == end_state_passes

        for question, passed in values.items():
            df.loc[candidate.id, question.id] = passed

df.dropna(axis=0, inplace=True)

print(df)


data = learn.DataPair(target=df['passed'])

df.drop('passed', axis=1, inplace=True)

data.features = df
data = new_balance(data)

#total_trivial = 0
for y, (idx, row) in zip(data.target, data.features.iterrows()):
    trivial_rule = row[40] + row[41] + row[42] + row[43] + row[44] > 4
    #total_trivial += trivial_rule == y

importance = pd.DataFrame(columns=list(df))
cross_val_scores_array = []
for seed in range(20):

    X_train, X_test, y_train, y_test = train_test_split(data.features, list(data.target),
                                                        test_size=0.3,
                                                        random_state=seed)

    model = RandomForestClassifier(max_depth=4, n_estimators=10)
    parameters = {'max_depth': (2, 4, 8, 16), 'n_estimators': [5, 10, 20, 40, 80]}

    grid_model = GridSearchCV(model, parameters, n_jobs=1)
    grid_model.fit(X_train, y_train)

    print('optimal params: ' + str(grid_model.best_params_))

    model = RandomForestClassifier(max_depth=grid_model.best_params_['max_depth'],
                                   n_estimators=grid_model.best_params_['n_estimators'])
    model.fit(X_train, y_train)

    c = statistics.mean([float(e) for e in cross_val_score(model, X_test, y_test, scoring='accuracy')])
    cross_val_scores_array.append(c)

    p = model.feature_importances_
    importance = importance.append({col: value for col, value in zip(list(df), p)}, ignore_index=True)

print('importance avg: ' + str(importance.mean()))
print('importance std: ' + str(importance.std()))

print('Confusion Matrix:')
test_prediction = model.predict(X_test)
print(confusion_matrix(y_test, test_prediction))

#trivial_accuracy = total_base / data.features.shape[0]
trivial_accuracy = right_base / total_base

print('trivial accuracy: ' + str(trivial_accuracy))

cross_val = statistics.mean(cross_val_scores_array)
print('delta (cross_val - trivial): ' + str(cross_val - trivial_accuracy))
print('avg cross val: ' + str(cross_val))
print('std cross val: ' + str(statistics.stdev(cross_val_scores_array)))
