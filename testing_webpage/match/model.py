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


from match.pickle_models.pickle_handler import save_model, load_model
from match import common_learning, learn, text_match, clustering
from subscribe import helper as h
from match.pickle_models import pickle_handler


DIR_PATH = os.path.dirname(os.path.realpath(__file__))


def load_data_for_prediction():
    """
    Loads and prepares all data.
    :return: data DataFrame with features and target.
    """
    data, candidates = common_learning.load_data()
    return data, candidates


def predict_and_save(data, model, candidates):

    data['prediction'] = model.predict(data)

    for candidate, (pk, row) in zip(candidates, data.iterrows()):
        candidate.match_classification = int(row['prediction'])

        #from django.utils.encoding import smart_text
        # Encoding prevents error when screening_explanation has special chars.
        #candidate.screening_explanation = smart_text(candidate.screening_explanation)
        candidate.save()


def learn_and_predict():
    """
    Predict matches and stores them on the candidates.
    :return: None
    """

    model, _ = learn.get_model()
    save_model(model)
    data, candidates = load_data_for_prediction()
    predict_and_save(data, model, candidates)


def predict_match(candidates):
    """
    Given candidates predict their match.
    :param candidates: Can be either a list of candidates or a single candidate.
    :return: None
    """
    model = load_model()
    return common_learning.predict_property(candidates, model)


def predict_match_and_save(candidates):
    predictions, candidates = predict_match(candidates)

    for p, c in zip(predictions, candidates):
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
    pickle_handler.save_defaults(defaults)
    data = common_learning.fill_missing_values(data)
    data = common_learning.add_synthetic_fields(data)

    # Order is key, Hashers are calculated before hashing the data.
    save_hashers(data)
    data = common_learning.hash_columns(data, common_learning.get_hashing_info())

    # Order is key, save scaler, then scale
    #common_learning.get_scaler_and_save(data)
    #data = common_learning.scale(data)

    # Order is key: 1. filter for SELECTED_FIELDS 2. save scaler, 3. then scale
    #clustering_data = common_learning.filter_fields(data, clustering.SELECTED_FIELDS)
    #common_learning.get_scaler_and_save(clustering_data, fields=clustering.SELECTED_FIELDS)
    #clustering_data = common_learning.scale(clustering_data)


def save_hashers(data):
    for field, num_features in common_learning.get_hashing_info().items():
        _, hasher = common_learning.get_hashed_matrix_and_hasher(data, field, num_features)
        pickle_handler.save_hasher(hasher, field)


def do_your_stuff():
    text_match.update()
    learn_and_predict()
    save_other_values()


def run():
    sys.stdout = h.Unbuffered(open('model.log', 'a'))
    do_your_stuff()


if __name__ == '__main__':
    do_your_stuff()
