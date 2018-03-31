"""
Calculates a match value with learning algorithm
"""
from sklearn import svm
import statistics
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, mean_absolute_error
from imblearn.over_sampling import ADASYN

from match import common_learning#, xgboost_scikit_wrapper


NON_REJECTED_HONEY = 0.3  # ie better than backlog


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


def prepare_train_test(data, regression=True):
    """
    From splitting to removing Nan, routine tasks.
    :param data: dataframe
    :param regression: boolean
    :return: train and test tuple
    """

    train = DataPair()
    test = DataPair()
    train.features, train.target, test.features, test.target = get_train_test(data, 0.7)

    if not regression:
        train = balance(train)
        test = balance(test)

    return train, test


def get_train_test(data, train_percent):

    msk = np.random.rand(len(data)) < train_percent
    train = data[msk]
    test = data[~msk]
    return train.drop('target', axis=1), train['target'], test.drop('target', axis=1), test['target']


def my_accuracy(a, b):
    return statistics.mean([int(e1 == e2) for e1, e2 in zip(a, b)])


def load_target(data, regression, candidates):
    """
    :param data: the X
    :param regression: boolean
    :param candidates: list of candidates
    :return:
    """

    data['target'] = [common_learning.get_target_for_candidate(c) for c in candidates]
    data = data[[not pd.isnull(t) for t in data['target']]]
    if not regression:
        data['target'] = data['target'].apply(lambda y: 1 if y > NON_REJECTED_HONEY else 0)

    return data


def load_data_for_learning(regression=True):
    """
    Loads and prepares all data.
    :return: data DataFrame with features and target.
    """
    data, candidates = common_learning.load_data()
    data = load_target(data, regression, candidates)

    return data


class Result:
    def __init__(self, train_metric, test_metric, baseline_test_metric, regression=False):
        self.train_metric = train_metric
        self.test_metric = test_metric
        self.baseline_test_metric = baseline_test_metric
        if regression:
            self.improvement = self.baseline_test_metric - self.test_metric
        else:
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


def learn_model(train, regression=True, xgboost=False):

    # TODO: missing xgboost; has bugs. Missing hard instalation on Linux also. Or using conda.
    # TODO: grid_search(model, train_set, train_target)
    if xgboost:

        params = {
            'max_depth': 3,  # the maximum depth of each tree
            'eta': 0.3,  # the training step for each iteration
            'silent': 1,  # logging mode - quiet
            'objective': 'binary:logistic',  # error evaluation for multiclass training
            'num_class': 2}  # the number of classes that exist in this dataset

        #model = xgboost_scikit_wrapper.XGBoostClassifier(num_boost_round=20, params=params)

    else:
        if regression:
            model = svm.SVR()
        else:
            model = svm.SVC(C=1.0, cache_size=200, class_weight=None, coef0=0.0,
                            decision_function_shape='ovr', degree=3, gamma='auto', kernel='rbf',
                            max_iter=-1, probability=False, random_state=None, shrinking=True,
                            tol=0.001, verbose=False)

    model.fit(train.features, train.target)
    return model


def my_mode(target):
    """
    Returns 1 for balanced sets (where there are excatly the same number of 1s and 0s)
    :param target: list of 1s and 0s
    :return: the mode
    """
    try:
        return statistics.mode(target)
    except statistics.StatisticsError:
        return 1


def eval_model(model, train, test, regression=True):

    train_prediction = model.predict(train.features)
    test_prediction = model.predict(test.features)

    """
    metrics.explained_variance_score(y_true, y_pred)	Explained variance regression score function
    metrics.mean_absolute_error(y_true, y_pred)	Mean absolute error regression loss
    metrics.mean_squared_error(y_true, y_pred[, …])	Mean squared error regression loss
    metrics.mean_squared_log_error(y_true, y_pred)	Mean squared logarithmic error regression loss
    metrics.median_absolute_error(y_true, y_pred)	Median absolute error regression loss
    metrics.r2_score(y_true, y_pred[, …])	R^2 (coefficient of determination) regression score function.
    """

    if regression:
        f = mean_absolute_error
    else:
        f = accuracy_score

    train_metric = f(train_prediction, train.target)
    test_metric = f(test_prediction, test.target)

    if regression:
        baseline_test_metric = f([statistics.mean(test.target) for _ in range(len(test.target))], test.target)
    else:
        baseline_test_metric = f([my_mode(test.target) for _ in test.target], test.target)

    if not regression:
        print('Confusion Matrix:')
        print(confusion_matrix(test.target, test_prediction))

    result = Result(train_metric, test_metric, baseline_test_metric, regression=regression)
    result.print()

    return result


def get_model(regression=True):
    """
    Calculates the match of each candidate, based on a learning algorithm.
    :return: model.
    """
    data = load_data_for_learning(regression=regression)

    train, test = prepare_train_test(data, regression=regression)

    model = learn_model(train, regression=regression)

    return model, eval_model(model, train, test, regression=regression)
