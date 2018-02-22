"""
Calculates a match value with learning algorithm
"""
import os
from django.core.wsgi import get_wsgi_application

# Environment can use the models as if inside the Django app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

import time
import sklearn
from sklearn.svm import SVR
import statistics
import numpy as np
import pandas as pd
from datetime import datetime
from dashboard.models import Candidate


def get_test_score(candidate, field, f):
    scores = [getattr(e, field) for e in candidate.evaluations.all()]
    if len(scores):
        return f(scores)
    else:
        return np.nan


def add_test_field(features, candidates, field):
    features['min_test_' + field] = [get_test_score(c, field, min) for c in candidates]
    features['median_test_' + field] = [get_test_score(c, field, statistics.median) for c in candidates]
    features['max_test_' + field] = [get_test_score(c, field, max) for c in candidates]
    return features


def add_test_features(features, candidates, fields):
    for f in fields:
        features = add_test_field(features, candidates, f)
    return features


def get_target(candidate):
    """
    3 possible values
    :param candidate:
    :return: 1 = Very Good Match, 0 = Bad match, np.nan = unknown
    """
    if candidate.state.code in ('GTJ', 'STC', ):  # Approved by client or by us.
        return 1
    elif candidate.state.code in ('ROI', 'RBC', 'SR'):  # Rejected by client or by us.
        return 0
    else:
        return np.nan


def get_accuracy(features, values, model):
    return sklearn.model_selection.cross_val_score(model, features, values, scoring='accuracy').mean()


def get_train_test(data, train_percent):
    msk = np.random.rand(len(data)) < train_percent
    train = data[msk]
    test = data[~msk]
    return train.drop('target', axis=1), train['target'], test.drop('target', axis=1), test['target']


def fill_missing_values(data):

    data['text_match'].fillna(statistics.median(data['text_match']), inplace=True)
    data['education'].fillna(statistics.mode(data['education']), inplace=True)
    #data['profession'].fillna(statistics.mode(data['profession']), inplace=True)

    for column in data.columns.values:
        if 'test' in column:
            data[column].fillna(statistics.median(data[column]), inplace=True)

    return data


def calculate_all_candidates_match():
    """
    Calculates the match of each candidate, based on a learning algorithm.
    :return:
    """
    data = pd.DataFrame()

    candidates = Candidate.objects.all()

    # TODO: add index as the candidate.pk
    data['text_match'] = [c.text_match for c in candidates]
    data['education'] = [c.get_education_level() for c in candidates]
    data['profession'] = [c.get_profession_name() for c in candidates]
    data = pd.get_dummies(data, columns=["profession"])
    #data.drop('profession', axis=1, inplace=True)

    data = add_test_features(data, candidates, ['passed', 'final_score'])

    data['target'] = [get_target(c) for c in candidates]
    data = data[[t is not None for t in data['target']]]

    #data.drop(data[data.target > 0].index, inplace=True)

    train_features, train_target, test_features, test_target = get_train_test(data, 0.8)

    train_features = fill_missing_values(train_features)
    test_features = fill_missing_values(test_features)

    model = SVR(kernel='rbf', C=1e3, gamma=0.001)

    print(train_features)
    print(train_target)

    model.fit(train_features, train_target)
    # model.fit(data_tf_idf_train, train_target_values, nb_epoch=EPOCHS, batch_size=BATCH_SIZE)

    # grid_search(model, train_set, train_target)

    print('TRAIN ACCURACY: ' + str(get_accuracy(train_features, train_target, model)))
    print('TEST ACCURACY: ' + str(get_accuracy(test_features, test_target, model)))


if __name__ == '__main__':
    t0 = time.time()
    calculate_all_candidates_match()
    t1 = time.time()
    print('On {0} CANDIDATE_MATCH, took: {1}'.format(datetime.today(), t1 - t0))
