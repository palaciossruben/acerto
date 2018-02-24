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

from dashboard.models import Candidate


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
            return np.nan


def load_data():
    """
    Loads and prepares all data.
    :return: data DataFrame with features and target + candidates.
    """
    data = pd.DataFrame()

    candidates = Candidate.objects.all()

    data['text_match'] = [c.text_match for c in candidates]
    data['education'] = [c.get_education_level() for c in candidates]
    data['profession'] = [c.get_profession_name() for c in candidates]
    data = pd.get_dummies(data, columns=["profession"])

    data = add_test_features(data, candidates, ['passed', 'final_score'])

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

    data['text_match'].fillna(np.nanmedian(data['text_match']), inplace=True)
    data['education'].fillna(np.nanmedian(data['education']), inplace=True)

    for column in data.columns.values:
        if 'test' in column:
            data[column].fillna(np.nanmedian(data[column]), inplace=True)

    return data
