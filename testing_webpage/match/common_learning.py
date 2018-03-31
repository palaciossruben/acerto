"""
Common for learning and prediction tasks
"""
import os
from django.core.wsgi import get_wsgi_application

# Environment can use the models as if inside the Django app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

import pickle
import statistics
import numpy as np
import pandas as pd

from dashboard.models import Candidate, State
from sklearn.feature_extraction import FeatureHasher


DIR_PATH = os.path.dirname(os.path.realpath(__file__))


def get_test_score(candidate, field, f):
    scores = [float(getattr(e, field)) for e in candidate.evaluations.all()]
    if len(scores):
        return f(scores)
    else:
        return np.nan


def add_test_field(features, candidates, field):
    features['min_test_' + field] = [get_test_score(c, field, min) for c in candidates]
    features['median_test_' + field] = [get_test_score(c, field, statistics.median) for c in candidates]
    features['mean_test_' + field] = [get_test_score(c, field, statistics.mean) for c in candidates]
    features['max_test_' + field] = [get_test_score(c, field, max) for c in candidates]
    return features


def add_test_features(features, candidates, fields):
    for f in fields:
        features = add_test_field(features, candidates, f)
    return features


def get_target_for_candidate(candidate):
    """
    3 possible values
    :param candidate:
    :return: 1 = Very Good Match, 0 = Bad match, np.nan = unknown
    """
    if candidate.screening is not None:
        return int(candidate.screening.passed)
    else:
        if candidate.state.code in ('GTJ', 'STC', ):  # Approved by client or by us.
            return 1
        elif candidate.state.code in ('ROI', 'RBC', 'SR'):  # Rejected by client or by us.
            return 0
        else:
            max_honey = max({s.honey for s in State.objects.all()})
            return candidate.state.honey/max_honey


def get_hashing_info():
    """
    Add new hashing fields here.
    :return: a hashing dict, with key=field_name, value=num_features
    """
    hashing_info = dict()
    hashing_info['profession'] = 10
    hashing_info['campaign'] = 20
    return hashing_info


def hash_columns(data):
    hashing_info = get_hashing_info()
    for field, num_features in hashing_info.items():
        data = hash_column(data, field, num_features)

    return data


def load_raw_data(candidates=Candidate.objects.all()):
    data = pd.DataFrame()

    # campaign should be treated categorically
    data['campaign'] = [str(c.campaign.pk) for c in candidates]
    data['text_match'] = [c.text_match for c in candidates]
    data['education'] = [c.get_education_level() for c in candidates]
    data['profession'] = [c.get_profession_name() for c in candidates]
    data = add_test_features(data, candidates, ['passed', 'final_score'])

    return data


def load_data(candidates=Candidate.objects.all()):
    """
    Loads and prepares all data.
    :return: data DataFrame with features and target + candidates.
    """
    data = load_raw_data(candidates)
    data = fill_missing_values(data)
    data = hash_columns(data)

    return data, candidates


def get_nan_percentages(df):
    """

    :param df: DataFrame
    :return:
    """
    d = dict()
    for c in df.columns.values:
        d[c] = np.mean(pd.isnull(df[c]))

    return d


def calculate_defaults(data):

    defaults = dict()

    defaults['profession'] = statistics.mode(data['profession'])
    defaults['text_match'] = np.nanmedian(data['text_match'])
    defaults['education'] = np.nanmedian(data['education'])

    for column in data.columns.values:
        if 'test' in column:
            defaults[column] = np.nanmedian(data[column])

    return defaults


def save_defaults(defaults):
    pickle.dump(defaults, open(os.path.join(DIR_PATH, 'defaults.p'), "wb"))


def load_defaults():
    return pickle.load(open(os.path.join(DIR_PATH, 'defaults.p'), "rb"))


def fill_missing_values(data, defaults=None):

    if defaults is None:
        defaults = calculate_defaults(data)

    data['profession'].fillna(defaults['profession'], inplace=True)
    data['text_match'].fillna(defaults['text_match'], inplace=True)
    data['education'].fillna(defaults['education'], inplace=True)

    for column in data.columns.values:
        if 'test' in column:
            data[column].fillna(defaults[column], inplace=True)

    return data


def get_hasher(num_features):
    return FeatureHasher(n_features=num_features, non_negative=False, input_type='string')


def add_hashed_matrix_to_data(matrix, data, column_name, num_features):
    hashed_df = pd.DataFrame(matrix.toarray())

    for i in range(num_features):
        data[column_name + '_' + str(i)] = list(hashed_df[i])

    # Finally, remove old column
    data.drop(column_name, axis=1, inplace=True)
    return data


def hash_column(data, column_name, num_features):
    """uses the hash trick to encode many categorical values in few dimensions."""

    matrix = get_hasher(num_features).fit_transform(data[column_name])
    return add_hashed_matrix_to_data(matrix, data, column_name, num_features)
