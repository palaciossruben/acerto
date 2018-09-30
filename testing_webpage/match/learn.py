"""
Calculates a match value with learning algorithm
"""
import statistics
import numpy as np
import pandas as pd
import re
from sklearn.metrics import accuracy_score
from imblearn.over_sampling import ADASYN
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, cross_val_score
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import confusion_matrix
from sklearn.utils import resample

from dashboard.models import Candidate
from match import common_learning

# make reproducible results
np.random.seed(seed=0)


PARAMS = {'n_estimators': [10, 50, 200], 'max_depth': [5, 15, 30]}
CLASS_WEIGHTS = {0: 1, 1: 1}
TARGET = 'target'
DATA_SPLIT_RATE = 0.8


def synthetic_balance(data):
    """
    Balances samples with ADASYN algorithm:
    http://sci2s.ugr.es/keel/pdf/algorithm/congreso/2008-He-ieee.pdf
    :param data: the dataframe
    :return: balanced dataframe
    """

    target = data[TARGET]
    features = data.drop(TARGET, axis=1)

    print('unbalanced positive weight: ' + str(np.mean(target)))

    # Apply the random over-sampling
    ada = ADASYN()
    try:
        features, target = ada.fit_sample(features, target)
    except ValueError:  # ValueError: No samples will be generated with the provided ratio settings.
        pass

    print('balanced positive weight: ' + str(np.mean(target)))

    columns = list(data)
    columns.remove(TARGET)
    data = pd.DataFrame(features, columns=columns)
    data.loc[:, TARGET] = target
    return data


def resample_balance(data):
    """
    Basic Over sampling to balance classes
    :param data:
    :return:
    """
    # There will always be more rejected than recommended
    majority = data[data[TARGET] == 0]
    minority = data[data[TARGET] == 1]

    # Up sample minority class
    minority_up_sampled = resample(minority,
                                   replace=True,  # sample with replacement
                                   n_samples=majority.shape[0],  # to match majority class
                                   random_state=123)

    return pd.concat([majority, minority_up_sampled])


def split_data(data, train_percent):
    """
    CAn work with or without candidates, either has 2 or 4 outputs
    :param data:
    :param train_percent:
    :return:
    """

    data = data.copy()  # copies to avoid the annoying copy dataframe warning
    msk = np.random.rand(data.shape[0]) < train_percent
    return data[msk], data[~msk]


def my_accuracy(a, b):
    return statistics.mean([int(e1 == e2) for e1, e2 in zip(a, b)])


def load_target(data):
    """
    :param data: the X
    :return:
    """

    data.loc[:, TARGET] = [common_learning.get_target_for_candidate(Candidate.objects.get(pk=candidate_idx))
                           for candidate_idx in data.index]
    data = data[[not pd.isnull(t) for t in data[TARGET]]]

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

    y_prediction = cross_val_predict(clf, train.features, train.target, cv=3)

    cv_accuracy = get_cv_scores(clf, train)

    print()
    print()
    print('ON TRAIN DATA:')
    print_confusion_matrix(train.target, y_prediction)
    print('cv accuracy is: {}'.format(cv_accuracy))
    print('cv mean accuracy is: {}%'.format(np.round(np.mean(cv_accuracy)*100, 2)))

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


def get_values(my_confusion_matrix):

    my_confusion_matrix = pd.DataFrame(my_confusion_matrix)

    FP = my_confusion_matrix.sum(axis=0) - np.diag(my_confusion_matrix)  # False positives
    FN = my_confusion_matrix.sum(axis=1) - np.diag(my_confusion_matrix)  # False negatives
    TP = np.diag(my_confusion_matrix)  # True positives
    TN = my_confusion_matrix.values.sum() - (FP + FN + TP)  # True negatives

    return FP, FN, TP, TN


def get_false_positive_rate(FP, TN):
    """
    Takes the [1] element as we are interested in the positive class, only
    :param FN: False Negatives, Series
    :param TP: True Positive, Series
    :return:
    """
    return round(FP / (FP + TN) * 100, 2)[1]


def get_false_negative_rate(FN, TP):
    """
    Takes the [1] element as we are interested in the positive class, only
    :param FN: False Negatives, Series
    :param TP: True Positive, Series
    :return:
    """
    return round(FN / (TP + FN) * 100, 2)[1]


def print_confusion_matrix(y_true, y_prediction):

    print('Confusion Matrix:')
    cf = confusion_matrix(y_true, y_prediction)
    print(cf)

    FP, FN, TP, TN = get_values(cf)
    print('False positive rate: {}'.format(get_false_positive_rate(FP, TN)))
    print('False negative rate: {}'.format(get_false_negative_rate(FN, TP)))


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
    print()
    print()
    print('ON HOLD OUT DATA:')

    train_prediction = model.predict(train.features)
    test_prediction = model.predict(test.features)

    train_metric = accuracy_score(train_prediction, train.target)
    test_metric = accuracy_score(test_prediction, test.target)

    baseline_test_metric = accuracy_score([target_mode(test.target) for _ in test.target], test.target)

    print_confusion_matrix(test.target, test_prediction)

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


def get_balanced_data_pair(data):
    #data = resample_balance(data)
    data = synthetic_balance(data)

    data_pair = DataPair()
    data_pair.features = data.drop(TARGET, axis=1)
    data_pair.target = data[TARGET]
    return data_pair


def process_raw_data(data, defaults):
    data = common_learning.fill_missing_values(data, defaults=defaults)
    data = common_learning.add_synthetic_fields(data)
    data = load_target(data)
    return get_balanced_data_pair(data)


def get_model_with_strict_eval(train, hold_out):

    print('size of train after split: {}'.format(train.shape[0]))
    print('size of hold out split: {}'.format(hold_out.shape[0]))

    defaults = common_learning.calculate_defaults(train)

    train = process_raw_data(train, defaults)
    hold_out = process_raw_data(hold_out, defaults)

    model = learn_model(train)
    print_feature_importance(model, train.features)

    eval_model(model, train=train, test=hold_out)

    return model


def get_model():
    """
    Calculates the match of each candidate, based on a learning algorithm.
    :return: model.
    """
    candidates = common_learning.get_filtered_candidates()
    data = common_learning.load_raw_data(candidates)
    print('size of raw data: {}'.format(data.shape[0]))

    # The hold_out is a pristine untouched data set
    train, hold_out = split_data(data, DATA_SPLIT_RATE)

    #candidate_idx = pd.Series(hold_out.index.values, index=hold_out.index.values)
    #wfi_filter = candidate_idx.apply(
    #    lambda idx: 'WFI' in [e.to_state.code for e in Candidate.objects.get(pk=idx).state_events.all()])
    #wfi_test = hold_out[wfi_filter]

    model = get_model_with_strict_eval(train, hold_out)

    # train with all what you have: MAKE SURE THIS IS DONE AT THE END
    defaults = common_learning.calculate_defaults(data)
    data = process_raw_data(data, defaults)
    model.fit(data.features, data.target)
    return model
