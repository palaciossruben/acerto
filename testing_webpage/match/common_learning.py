"""
Common for learning and prediction tasks
"""
import os
from django.core.wsgi import get_wsgi_application

# Environment can use the models as if inside the Django app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

import statistics
import numpy as np
import pandas as pd

from dashboard.models import Candidate, State
from sklearn.feature_extraction import FeatureHasher


def get_test_score(candidate, field, f):
    scores = [float(getattr(e, field)) for e in candidate.evaluations.all()]
    if len(scores):
        return f(scores)
    else:
        return np.nan


def add_test_field(features, candidates, field):
    features['min_test_' + field] = [get_test_score(c, field, min) for c in candidates]
    features['median_test_' + field] = [get_test_score(c, field, statistics.median) for c in candidates]
    features['max_test_' + field] = [get_test_score(c, field, max) for c in candidates]
    return features


def add_test_features(features, candidates, fields):
    for f in fields:
        features = add_test_field(features, candidates, f)
    return features


def get_target(candidate):
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


def load_data():
    """
    Loads and prepares all data.
    :return: data DataFrame with features and target + candidates.
    """
    data = pd.DataFrame()

    candidates = Candidate.objects.all()

    # campaign should be treated categorically
    data['campaign'] = [str(c.campaign.pk) for c in candidates]
    data['text_match'] = [c.text_match for c in candidates]
    data['education'] = [c.get_education_level() for c in candidates]
    data['profession'] = [c.get_profession_name() for c in candidates]
    data = add_test_features(data, candidates, ['passed', 'final_score'])

    data = fill_missing_values(data)

    data = hash_column(data, 'profession', 10)
    data = hash_column(data, 'campaign', 20)

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


def fill_missing_values(data):

    data['profession'].fillna(statistics.mode(data['profession']), inplace=True)
    data['text_match'].fillna(np.nanmedian(data['text_match']), inplace=True)
    data['education'].fillna(np.nanmedian(data['education']), inplace=True)

    for column in data.columns.values:
        if 'test' in column:
            data[column].fillna(np.nanmedian(data[column]), inplace=True)

    return data


def hash_column(data, column_name, num_features):
    """uses the hash trick to encode many categorical values in few dimensions."""

    hasher = FeatureHasher(n_features=num_features, non_negative=False, input_type='string')
    X_new = hasher.fit_transform(data[column_name])
    hashed_df = pd.DataFrame(X_new.toarray())

    for i in range(num_features):
        data[column_name + '_' + str(i)] = list(hashed_df[i])

    # Finally, remove old column
    data.drop(column_name, axis=1, inplace=True)

    return data
