"""
Calculates a match value with learning algorithm
"""
import os
from django.core.wsgi import get_wsgi_application

# Environment can use the models as if inside the Django app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

import time
import pickle
import random
from sklearn.model_selection import cross_val_score
from sklearn import svm
import statistics
import numpy as np
import pandas as pd
from sklearn import metrics
from datetime import datetime
from imblearn.over_sampling import ADASYN

import common_learning


def balance(data):
    """
    Balances samples with ADASYN algorithm:
    http://sci2s.ugr.es/keel/pdf/algorithm/congreso/2008-He-ieee.pdf
    :param train_features: X
    :param train_target: y
    :return: train_features, train_target
    """

    print('unbalanced positive weight: ' + str(np.mean(data.target)))

    # Apply the random over-sampling
    ada = ADASYN()
    data.features, data.target = ada.fit_sample(data.features, data.target)

    print('balanced positive weight: ' + str(np.mean(data.target)))

    return data


def prepare_train_test(data):
    """
    From splitting to removing Nan, routine tasks.
    :param data:
    :return:
    """

    train = DataPair()
    test = DataPair()
    train.features, train.target, test.features, test.target = get_train_test(data, 0.7)

    train.features = common_learning.fill_missing_values(train.features)
    test.features = common_learning.fill_missing_values(test.features)

    train = balance(train)
    test = balance(test)

    return train, test


def get_accuracy(features, target, model):
    scores = cross_val_score(model, features, target.astype(int), scoring='accuracy').mean()
    return scores.mean(), scores.std() * 2


def get_train_test(data, train_percent):
    msk = np.random.rand(len(data)) < train_percent
    train = data[msk]
    test = data[~msk]
    return train.drop('target', axis=1), train['target'], test.drop('target', axis=1), test['target']


def my_accuracy(a, b):
    return statistics.mean([int(e1 == e2) for e1, e2 in zip(a, b)])


def load_data_for_learning():
    """
    Loads and prepares all data.
    :return: data DataFrame with features and target.
    """
    data, candidates = common_learning.load_data()

    data['target'] = [common_learning.get_target(c) for c in candidates]
    data = data[[not pd.isnull(t) for t in data['target']]]
    data['target'] = data['target'].apply(lambda y: int(y))

    print('PERCENTAGE OF NULL BY COLUMN: ' + str(common_learning.get_nan_percentages(data)))

    return data


class DataPair:
    def __init__(self, features=None, target=None):
        self.features = features
        self.target = target


def learn_model(train):
    # TODO: grid_search(model, train_set, train_target)
    model = svm.SVC()
    model.fit(train.features, train.target)
    return model


def eval_model(model, train, test):
    print('TRAIN ACCURACY: {0} (+/- {1})'.format(*get_accuracy(train.features, train.target, model)))
    print('TEST ACCURACY: {0} (+/- {1})'.format(*get_accuracy(test.features, test.target, model)))

    predicted_target = model.predict(test.features)
    print('MY TEST ACCURACY: ' + str(my_accuracy(predicted_target, test.target)))
    print('RANDOM TEST ACCURACY: ' + str(my_accuracy([random.randint(0, 1) for _ in test.target], test.target)))

    print('Confusion Matrix:')
    print(metrics.confusion_matrix(test.target, predicted_target))


def calculate_all_candidates_match():
    """
    Calculates the match of each candidate, based on a learning algorithm.
    :return:
    """
    data = load_data_for_learning()

    train, test = prepare_train_test(data)

    model = learn_model(train)

    eval_model(model, train, test)

    pickle.dump(model, open("match_model.p", "wb"))


if __name__ == '__main__':
    t0 = time.time()
    calculate_all_candidates_match()
    t1 = time.time()
    print('On {0} CANDIDATE_MATCH, took: {1}'.format(datetime.today(), t1 - t0))
