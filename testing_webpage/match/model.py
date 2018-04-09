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

import pickle

from match import common_learning, learn, text_match
from dashboard.models import Candidate
from subscribe import helper as h

DIR_PATH = os.path.dirname(os.path.realpath(__file__))


def load_data_for_prediction():
    """
    Loads and prepares all data.
    :return: data DataFrame with features and target.
    """
    data, candidates = common_learning.load_data()
    return data, candidates


def predict_and_save(data, model, candidates, regression=True):

    data['prediction'] = model.predict(data)

    for candidate, (pk, row) in zip(candidates, data.iterrows()):
        if regression:
            candidate.match_regression = row['prediction']
        else:
            candidate.match_classification = int(row['prediction'])

        #from django.utils.encoding import smart_text
        # Encoding prevents error when screening_explanation has special chars.
        #candidate.screening_explanation = smart_text(candidate.screening_explanation)
        candidate.save()


def save_model(regression, model):
    if regression:
        common_learning.save_object(model, 'regression_model.p')
    else:
        common_learning.save_object(model, 'classifier_model.p')


def load_model(regression=True):
    if regression:
        return common_learning.load_object('regression_model.p')
    else:
        return common_learning.load_object('classifier_model.p')


def learn_and_predict(regression=True):
    """
    Predict matches and stores them on the candidates.
    :return: None
    """

    model, _ = learn.get_model(regression=regression)
    save_model(regression, model)
    data, candidates = load_data_for_prediction()
    predict_and_save(data, model, candidates, regression=regression)


def predict_match(candidates, regression=True):
    """
    Given candidates predict their match.
    :param candidates: Can be either a list of candidates or a single candidate.
    :param regression: boolean
    :return: None
    """
    model = load_model(regression=regression)
    return common_learning.predict_property(candidates, model)


def predict_match_and_save(candidates, regression=True):
    predictions, candidates = predict_match(candidates, regression=regression)

    for p, c in zip(predictions, candidates):
        if regression:
            c.match_regression = p
        else:
            c.match_classification = p
        c.save()


def save_other_values():
    """
    Saves default field values and hashes for real time prediction later on.
    :return: None
    """

    data = common_learning.load_raw_data()

    # Order is key here. Defaults are calculated before fill_missing_values, as this process uses the defaults.
    defaults = common_learning.calculate_defaults(data)
    common_learning.save_defaults(defaults)
    data = common_learning.fill_missing_values(data)

    # Order is key, Hashers are calculated before hashing the data.
    save_hashers(data)
    data = common_learning.hash_columns(data, common_learning.get_hashing_info())

    # Order is key, save scaler, then scale
    common_learning.save_scaler(data)
    data = common_learning.scale(data)


def save_hashers(data):
    for field, num_features in common_learning.get_hashing_info().items():
        _, hasher = common_learning.get_hashed_matrix_and_hasher(data, field, num_features)
        common_learning.save_object(hasher, common_learning.get_hasher_name(field))


def run():

    sys.stdout = h.Unbuffered(open('model.log', 'a'))

    text_match.update()
    learn_and_predict(regression=False)
    learn_and_predict(regression=True)
    save_other_values()


if __name__ == '__main__':
    run()
