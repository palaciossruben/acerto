"""
Learns a new model and predicts forecast values.
"""
import os
import sys

from django.core.wsgi import get_wsgi_application

# Environment can use the models as if inside the Django app
sys.path.insert(0, '/'.join(os.getcwd().split('/')[:-1]))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

import time
import pickle
from datetime import datetime

from match import common_learning, learn, text_match
from dashboard.models import Candidate


DIR_PATH = os.path.dirname(os.path.realpath(__file__))


def load_data_for_prediction():
    """
    Loads and prepares all data.
    :return: data DataFrame with features and target.
    """
    data, candidates = common_learning.load_data()
    print('PERCENTAGE OF NULL BY COLUMN: ' + str(common_learning.get_nan_percentages(data)))
    return data, candidates


def predict_and_save(data, model, candidates):

    data['prediction'] = model.predict(data)

    for candidate, (pk, row) in zip(candidates, data.iterrows()):
        candidate.match = row['prediction']
        candidate.save()


def save_model(regression, model):
    if regression:
        pickle.dump(model, open(get_path('regression_model.p'), "wb"))
    else:
        pickle.dump(model, open(get_path('classifier_model.p'), "wb"))


def load_model(regression=True):
    if regression:
        return pickle.load(open(get_path('regression_model.p'), "rb"))
    else:
        return pickle.load(open(get_path('classifier_model.p'), "rb"))


def learn_and_predict(regression=True):
    """
    Predict matches and stores them on the candidates.
    :return: None
    """

    model, _ = learn.get_model(regression=regression)
    save_model(regression, model)
    data, candidates = load_data_for_prediction()
    predict_and_save(data, model, candidates)


def predict_match(candidates, regression=True):
    """
    Given candidates predict their match.
    :param candidates: Can be either a list of candidates or a single candidate.
    :param regression: boolean
    :return: None
    """
    if isinstance(candidates, Candidate):
        candidates = [candidates]

    data = common_learning.load_raw_data(candidates)
    data = common_learning.fill_missing_values(data, defaults=common_learning.load_defaults())
    data = add_hash_fields_from_saved_hashes(data)
    model = load_model(regression=regression)
    return model.predict(data), candidates


def save_other_values():
    """
    Saves default field values and hashes for real time prediction later on.
    :return: None
    """

    data = common_learning.load_raw_data()
    data = common_learning.fill_missing_values(data)
    defaults = common_learning.calculate_defaults(data)
    common_learning.save_defaults(defaults)

    save_hashers(data)


def get_path(file_name):
    return os.path.join(DIR_PATH, file_name)


def get_hasher_path(field):
    return get_path("hasher_{}.p".format(field))


def save_hashers(data):
    for field, num_features in common_learning.get_hashing_info().items():
        hasher = common_learning.get_hasher(num_features)
        hasher.fit_transform(data[field])
        pickle.dump(hasher, open(get_hasher_path(field), "wb"))


def add_hash_fields_from_saved_hashes(data):
    for field, num_features in common_learning.get_hashing_info().items():
        hasher = pickle.load(open(get_hasher_path(field), "rb"))
        hashed_x = hasher.transform(data[field])
        data = common_learning.add_hashed_matrix_to_data(hashed_x, data, field, num_features)

    return data


if __name__ == '__main__':
    t0 = time.time()
    text_match.update()

    # save a classification model first:
    model, _ = learn.get_model(regression=False)
    save_model(False, model)

    # do complete stuff (learn, predict and save for whole DB) with regression model
    learn_and_predict(regression=True)

    save_other_values()
    t1 = time.time()
    print('On {0} LEARN AND PREDICT_MATCH, took: {1}'.format(datetime.today(), t1 - t0))
