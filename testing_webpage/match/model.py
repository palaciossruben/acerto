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
    predict_and_save(data, model, candidates, regression=regression)


def predict_match(candidates, regression=True):
    """
    Given candidates predict their match.
    :param candidates: Can be either a list of candidates or a single candidate.
    :param regression: boolean
    :return: None
    """

    if isinstance(candidates, Candidate):
        candidates = [candidates]

    if not len(candidates):
        return [], []

    data = common_learning.load_raw_data(candidates)
    data = common_learning.fill_missing_values(data, defaults=common_learning.load_defaults())
    data = add_hash_fields_from_saved_hashes(data)
    model = load_model(regression=regression)
    return model.predict(data), candidates


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
        _, hasher = common_learning.get_hashed_matrix_and_hasher(data, field, num_features)
        pickle.dump(hasher, open(get_hasher_path(field), "wb"))


def get_matrix_from_saved_hash(data, field):
    data = common_learning.make_column_hashable(data, field)
    hasher = pickle.load(open(get_hasher_path(field), "rb"))
    return hasher.transform(data[field])


def add_hash_fields_from_saved_hashes(data):
    for field, num_features in common_learning.get_hashing_info().items():
        matrix = get_matrix_from_saved_hash(data, field)
        data = common_learning.add_hashed_matrix_to_data(matrix, data, field, num_features)

    return data


def run():

    sys.stdout = h.Unbuffered(open('model.log', 'a'))

    text_match.update()
    learn_and_predict(regression=False)
    learn_and_predict(regression=True)
    save_other_values()


if __name__ == '__main__':
    run()
