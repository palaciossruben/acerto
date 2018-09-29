"""
Calculates a match value with learning algorithm
"""
import statistics
import numpy as np
import pandas as pd
import re
from sklearn.metrics import accuracy_score, confusion_matrix
from imblearn.over_sampling import ADASYN
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, cross_val_score

from match import common_learning

# make reproducible results
np.random.seed(seed=0)


PARAMS = {'n_estimators': [90, 100, 110], 'max_depth': [17, 20, 23]}
CLASS_WEIGHTS = {0: 1, 1: 100}


def balance(data):
    """
    Balances samples with ADASYN algorithm:
    http://sci2s.ugr.es/keel/pdf/algorithm/congreso/2008-He-ieee.pdf
    :param data: the dataframe
    :return: train_features, train_target
    """

    print('unbalanced positive weight: ' + str(np.mean(data.target)))

    # Apply the random over-sampling
    ada = ADASYN()
    try:
        data.features, data.target = ada.fit_sample(data.features, data.target)
    except ValueError:  # ValueError: No samples will be generated with the provided ratio settings.
        pass

    print('balanced positive weight: ' + str(np.mean(data.target)))

    return data


def prepare_train_test(data):
    """
    From splitting to removing Nan, routine tasks.
    :param data: dataframe
    :return: train and test tuple
    """

    train = DataPair()
    test = DataPair()
    train.features, train.target, test.features, test.target = get_train_test(data, 0.7)

    return balance(train), balance(test)


def get_train_test(data, train_percent):

    msk = np.random.rand(len(data)) < train_percent
    train = data[msk]
    test = data[~msk]
    return train.drop('target', axis=1), train['target'], test.drop('target', axis=1), test['target']


def my_accuracy(a, b):
    return statistics.mean([int(e1 == e2) for e1, e2 in zip(a, b)])


def load_target(data, candidates):
    """
    :param data: the X
    :param candidates: list of candidates
    :return:
    """

    data['target'] = [common_learning.get_target_for_candidate(c) for c in candidates]
    data = data[[not pd.isnull(t) for t in data['target']]]

    return data


def load_data_for_learning():
    """
    Loads and prepares all data.
    :return: data DataFrame with features and target.
    """
    data, candidates = common_learning.load_data()
    data = load_target(data, candidates)
    return data


class Result:
    def __init__(self, train_metric, test_metric, baseline_test_metric):
        self.train_metric = train_metric
        self.test_metric = test_metric
        self.baseline_test_metric = baseline_test_metric
        self.improvement = self.test_metric - self.baseline_test_metric
        self.num_runs = 1

    def average_property(self, attribute, other_result):
        den = self.num_runs + other_result.num_runs
        value = (getattr(other_result, attribute) * other_result.num_runs + getattr(self,
                                                                                    attribute) * self.num_runs) / den
        setattr(self, attribute, value)

    def average(self, other_result):
        self.average_property('train_metric', other_result)
        self.average_property('test_metric', other_result)
        self.average_property('baseline_test_metric', other_result)
        self.average_property('improvement', other_result)
        self.num_runs += 1

    def get_nice_result(self, attr):
        return str(round(getattr(self, attr), 3) * 100)

    def print(self):
        print('TRAIN (%): ' + self.get_nice_result('train_metric'))
        print('TEST (%): ' + self.get_nice_result('test_metric'))
        print('BASELINE (%): ' + self.get_nice_result('baseline_test_metric'))
        print('IMPROVEMENT (%): ' + self.get_nice_result('improvement'))


class DataPair:
    def __init__(self, features=None, target=None):
        self.features = features
        self.target = target


def learn_model(train):

    # TODO: missing xgboost; has bugs. Missing hard instalation on Linux also. Or using conda.
    clf = GridSearchCV(RandomForestClassifier(random_state=0,
                                              class_weight=CLASS_WEIGHTS),
                       PARAMS,
                       cv=3,
                       verbose=1)
    clf.fit(train.features, train.target)

    cv_accuracy = get_cv_scores(clf, train)

    print('cv accuracy is: {}'.format(cv_accuracy))
    print('cv mean accuracy is: {}'.format(np.mean(cv_accuracy)))

    print('best params are:')
    print('max_depth {}'.format(clf.best_params_['max_depth']))
    print('n_estimators {}'.format(clf.best_params_['n_estimators']))

    return clf.best_estimator_


def target_mode(target):
    """
    Returns 1 for balanced sets (where there are exactly the same number of 1s and 0s)
    :param target: list of 1s and 0s
    :return: the mode
    """
    try:
        return statistics.mode(target)
    except statistics.StatisticsError:
        return 1


def print_confusion_matrix(test, test_prediction):

    print('Confusion Matrix:')
    my_confusion_matrix = confusion_matrix(test.target, test_prediction)
    print(my_confusion_matrix)

    total = sum(my_confusion_matrix[0]) + sum(my_confusion_matrix[1])

    print('false positives: {}%'.format(round(my_confusion_matrix[0][1]/total, 2) * 100))
    print('should minimize false negatives: {}%'.format(round(my_confusion_matrix[1][0]/total, 2)*100))


def percent_format(a_number):
    return round(a_number * 100, 1)


def get_cv_scores(model, data):

    scores = np.array(cross_val_score(estimator=model,
                                      X=data.features,
                                      y=data.target,
                                      cv=3,
                                      scoring='accuracy'))

    return np.array(scores)


def eval_model(model, train, test):

    train_prediction = model.predict(train.features)
    test_prediction = model.predict(test.features)

    train_metric = accuracy_score(train_prediction, train.target)
    test_metric = accuracy_score(test_prediction, test.target)

    baseline_test_metric = accuracy_score([target_mode(test.target) for _ in test.target], test.target)

    print_confusion_matrix(test, test_prediction)

    result = Result(train_metric, test_metric, baseline_test_metric)
    result.print()

    return result


def print_feature_importance(model, data):
    """
    It assumes the model is a RandomForest, for now
    :param model: sklearn model
    :param data: Dataframe
    :return:
    """
    iterator = reversed(sorted(zip(list(data), model.feature_importances_), key=lambda x: x[1]))
    importance = [e for e in iterator]
    importance_dict = dict()
    for key, value in importance:
        real_key = re.compile(r'_\d+').split(key)[0]
        importance_dict[real_key] = importance_dict.get(real_key, 0) + value

    importance_tuples = [(k, v) for k, v in importance_dict.items()]
    importance_tuples.sort(key=lambda x: x[1], reverse=True)

    print(importance_tuples)


def get_model():
    """
    Calculates the match of each candidate, based on a learning algorithm.
    :return: model.
    """
    data = load_data_for_learning()

    train, test = prepare_train_test(data)

    model = learn_model(train)

    # Used only for data exploration.
    print_feature_importance(model, data)

    return model, eval_model(model, train, test)
