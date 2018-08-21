"""
Calculates a match value with learning algorithm
"""
from sklearn import svm
import statistics
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, mean_absolute_error
from imblearn.over_sampling import ADASYN
from sklearn.ensemble import RandomForestClassifier

from match import common_learning
#from match import xgboost_scikit_wrapper

# make reproducible results
np.random.seed(seed=0)


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


def learn_model(train, xgboost=False):

    # TODO: missing xgboost; has bugs. Missing hard instalation on Linux also. Or using conda.
    # TODO: grid_search(model, train_set, train_target)
    if xgboost:

        params = {
            'max_depth': 3,  # the maximum depth of each tree
            'eta': 0.3,  # the training step for each iteration
            'silent': 1,  # logging mode - quiet
            'objective': 'binary:logistic',  # error evaluation for binary training
            'num_class': 2}  # the number of classes that exist in this data set

        #model = xgboost_scikit_wrapper.XGBoostClassifier(num_boost_round=20, params=params)

    else:
        model = RandomForestClassifier(max_depth=9,
                                       random_state=0,
                                       # guarantees that we do not miss many candidates with potential
                                       class_weight={0: 1, 1: 3}
                                       )

    model.fit(train.features, train.target)
    return model


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


def eval_model(model, train, test):

    train_prediction = model.predict(train.features)
    test_prediction = model.predict(test.features)

    f = accuracy_score

    train_metric = f(train_prediction, train.target)
    test_metric = f(test_prediction, test.target)

    baseline_test_metric = f([target_mode(test.target) for _ in test.target], test.target)

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
    print([e for e in iterator])


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
