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
from sklearn.preprocessing import StandardScaler
from match.pickle_models import pickle_handler
import common
from beta_invite import constants
from beta_invite.models import Test


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
    Contrast between very good and very bad candidates, where decisions have already been made explicitly
    No ambiguous states (such as Backlog, Did Interview etc.)
    :param candidate:
    :return: 1 = Very Good Match, 0 = Bad match, np.nan = unknown
    """
    if candidate.state in State.get_recommended_states():
        return 1
    elif candidate.state in State.get_rejected_states():
        return 0


def get_hashing_info():
    """
    Add new hashing fields here.
    :return: a hashing dict, with key=field_name, value=num_features
    """

    # Uncomment for high complexity
    hashing_info = dict()
    #hashing_info['campaign'] = 5
    hashing_info['candidate_country'] = 1
    hashing_info['candidate_city'] = 1
    hashing_info['campaign_country'] = 1
    hashing_info['campaign_city'] = 1
    hashing_info['profession'] = 1
    hashing_info['campaign_profession'] = 3
    hashing_info['gender'] = 1
    hashing_info['work_area'] = 1
    hashing_info['neighborhood'] = 1
    hashing_info['languages'] = 1
    hashing_info['dream_job'] = 1
    # TODO: ADD NEW FIELD HERE

    # TODO: different hashes for the same property, eg: candidate country and campaign country
    return hashing_info


def hash_columns(data, hashing_info):
    for field, num_features in hashing_info.items():
        data = hash_column(data, field, num_features)

    return data


def get_filtered_candidates():
    """Very good candidates contrasted with very bad ones"""
    return Candidate.objects.exclude(campaign_id=constants.DEFAULT_CAMPAIGN_ID)\
        .filter(state__in=State.get_recommended_states() + State.get_rejected_states())


"""
# TODO add new fields
    programs = models.CharField(max_length=250, null=True)
    address = models.CharField(max_length=100, null=True)
    profile = models.CharField(max_length=250, null=True)
    phone2 = models.CharField(max_length=40, null=True)
    phone3 = models.CharField(max_length=40, null=True)
    document = models.CharField(max_length=50, null=True)
    dream_job = models.CharField(max_length=50, null=True)
    hobbies = models.CharField(max_length=250, null=True)
    twitter = models.CharField(max_length=250, null=True)
    facebook = models.CharField(max_length=250, null=True)
    instagram = models.CharField(max_length=250, null=True)
    linkedin = models.CharField(max_length=250, null=True)
    photo_url = models.CharField(max_length=200, default='#')
    brochure_url = models.CharField(max_length=200, default='#')
    politics = models.BooleanField(default=False)
"""


def get_columns():
    return [#'campaign',
            'text_match',
            'candidate_country',
            'candidate_city',
            'campaign_country',
            'campaign_city',
            'profession',
            'campaign_profession',
            'education',
            'campaign_education',
            'gender',
            'work_area',
            # TODO: had only None, can add later on with more data
            #'salary',
            'neighborhood',
            'languages',
            'dream_job',
            ]


def from_list_to_query_set(candidates):
    """Efficiency reasons... do 1 query instead of thousands, later on"""
    return Candidate.objects.filter(pk__in=[c.pk for c in candidates])


def lower_str(text):
    if isinstance(text, str):
        return text.lower()
    else:
        return text


def load_raw_data(candidates=get_filtered_candidates()):

    if isinstance(candidates, list):
        candidates = from_list_to_query_set(candidates)

    # With QuerySet it is much faster.
    data_list = list(candidates.values_list(#'campaign_id',
                                            'text_match',
                                            'user__country_id',
                                            'user__city_id',
                                            'campaign__country_id',
                                            'campaign__city__id',
                                            'user__profession_id',
                                            'campaign__profession_id',
                                            'user__education__level',
                                            'campaign__education__level',
                                            'user__gender',
                                            'user__work_area',
                                            # TODO: had only None, can add later on with more data
                                            #'user__salary',
                                            'user__neighborhood',  # TODO: improve input
                                            'user__languages',  # TODO: improve input
                                            'user__dream_job',  # TODO: improve input

                                            # TODO: ADD NEW FIELD HERE
                                            ))

    data = pd.DataFrame(data_list, columns=get_columns())

    # Pre-Processing
    data['neighborhood'] = [lower_str(common.remove_accents(n)) for n in data['neighborhood']]
    data['languages'] = [lower_str(common.remove_accents(n)) for n in data['languages']]
    data['dream_job'] = [lower_str(common.remove_accents(n)) for n in data['dream_job']]

    # Calculated fields
    data['country_match'] = data['candidate_country'] == data['campaign_country']
    data['city_match'] = data['candidate_city'] == data['campaign_city']
    data['profession_match'] = data['campaign_profession'] == data['profession']
    data['education_match'] = data['campaign_education'] == data['education']
    data['min_education'] = data['campaign_education'] <= data['education']
    #data['open_field'] = [c.get_campaign_education_level() for c in candidates]

    # similar accuracy with high and low complexity:
    #data = add_test_features(data, candidates, ['passed', 'final_score'])
    data['median_test_final_score'] = [get_test_score(c, 'final_score', statistics.median) for c in candidates]


    #tests = Test.objects.all()

    #for t in tests:
    #    empty_array = np.empty((data.shape[0],))
    #    empty_array[:] = np.nan
    #    data[str(t.name) + 'median_final_score'] = empty_array
    """
    all_tests = dict()
    for c in candidates:
        test_score_dict = dict()
        for e in c.evaluations.all():
            for score in e.scores.all():
                current_value = test_score_dict.get(score.test.name)
                if current_value:
                    test_score_dict[score.test.name] = current_value.append(score.value)
                else:
                    test_score_dict[score.test.name] = [score.value]

        for k, v in test_score_dict.items():

            value = all_tests.get(k + 'median_final_score')
            if value:
                all_tests[k + 'median_final_score'] = value.append(np.median(v))
            else:
                all_tests[k + 'median_final_score'] = [np.median(v)]

    for k, v in all_tests.items():
        data[k] = v
    """

    return data


def filter_fields(data, selected_fields):
    """
    If selected_fields is not None then do the selection, otherwise do nothing
    :param data:
    :param selected_fields:
    :return:
    """
    if selected_fields:
        return data[selected_fields]
    else:
        return data


def load_data(candidates=get_filtered_candidates(),
              hashing_info=get_hashing_info(), selected_fields=None):
    """
    Loads and prepares all data.
    :return: data DataFrame with features and target + candidates.
    """
    data = load_raw_data(candidates)
    data = fill_missing_values(data)
    data = hash_columns(data, hashing_info)
    data = filter_fields(data, selected_fields)
    data = scale(data)

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


def right_mode(iterable):
    """
    All modes suck, defines the right one, ignoring nulls
    :return:
    """
    try:
        return statistics.mode([e for e in iterable if not pd.isnull(e)])
    except statistics.StatisticsError:  # triggered when mode performed over empty array
        return ''


def calculate_defaults(data):

    defaults = dict()

    defaults['text_match'] = np.nanmedian(data['text_match'])
    defaults['education'] = np.nanmedian(data['education'])
    defaults['candidate_country'] = right_mode(data['candidate_country'])
    defaults['candidate_city'] = right_mode(data['candidate_city'])
    defaults['campaign_country'] = right_mode(data['campaign_country'])
    defaults['campaign_city'] = right_mode(data['campaign_city'])
    defaults['profession'] = right_mode(data['profession'])
    defaults['campaign_profession'] = right_mode(data['campaign_profession'])
    defaults['education'] = np.nanmedian(data['education'])
    defaults['campaign_education'] = np.nanmedian(data['campaign_education'])
    defaults['gender'] = right_mode(data['gender'])
    defaults['work_area'] = right_mode(data['work_area'])
    defaults['neighborhood'] = right_mode(data['neighborhood'])
    defaults['languages'] = right_mode(data['languages'])
    defaults['dream_job'] = right_mode(data['dream_job'])
    # TODO: ADD NEW FIELD HERE

    # TODO: had only None, can add later on with more data
    # print(data['salary'])
    # defaults['salary'] = np.mean(data['salary'])

    for column in data.columns.values:
        if 'test' in column:
            defaults[column] = np.nanmedian(data[column])

    return defaults


def fill_missing_values(data, defaults=None):

    if defaults is None:
        defaults = calculate_defaults(data)

    data['text_match'].fillna(defaults['text_match'], inplace=True)
    data['education'].fillna(defaults['education'], inplace=True)
    data['candidate_country'].fillna(defaults['candidate_country'], inplace=True)
    data['candidate_city'].fillna(defaults['candidate_city'], inplace=True)
    data['campaign_country'].fillna(defaults['campaign_country'], inplace=True)
    data['campaign_city'].fillna(defaults['campaign_city'], inplace=True)
    data['profession'].fillna(defaults['profession'], inplace=True)
    data['campaign_profession'].fillna(defaults['campaign_profession'], inplace=True)
    data['campaign_education'].fillna(defaults['campaign_education'], inplace=True)
    data['gender'].fillna(defaults['gender'], inplace=True)
    data['work_area'].fillna(defaults['work_area'], inplace=True)
#    data['salary'].fillna(defaults['salary'], inplace=True)
    data['neighborhood'].fillna(defaults['neighborhood'], inplace=True)
    data['languages'].fillna(defaults['languages'], inplace=True)
    data['dream_job'].fillna(defaults['dream_job'], inplace=True)

    # TODO: ADD NEW FIELD HERE

    for column in list(data):
        if 'test' in column:
            data[column].fillna(defaults[column], inplace=True)

    """
    for column in list(data):
        if defaults.get(column):
            data[column].fillna(defaults[column], inplace=True)"""

    return data


def add_hashed_matrix_to_data(matrix, data, column_name, num_features):
    hashed_df = pd.DataFrame(matrix.toarray())

    for i in range(num_features):
        data[column_name + '_' + str(i)] = list(hashed_df[i])

    # Finally, remove old column
    data.drop(column_name, axis=1, inplace=True)
    return data


def make_column_hashable(data, column_name):
    if not isinstance(data.loc[0, column_name], str):
        data[column_name] = data[column_name].apply(lambda x: str(x))
    return data


def get_hashed_matrix_and_hasher(data, column_name, num_features):
    """
    1. If not str, convert to string
    2. Then will hash data and return matrix
    3. Also returns the fitted hash
    """

    data = make_column_hashable(data, column_name)

    hasher = FeatureHasher(n_features=num_features, non_negative=False, input_type='string')
    matrix = hasher.fit_transform(data[column_name])

    return matrix, hasher


def hash_column(data, column_name, num_features):
    """uses the hash trick to encode many categorical values in few dimensions."""

    matrix, _ = get_hashed_matrix_and_hasher(data, column_name, num_features)
    return add_hashed_matrix_to_data(matrix, data, column_name, num_features)


def get_matrix_from_saved_hash(data, field):
    data = make_column_hashable(data, field)
    hasher = pickle_handler.load_hasher(field)
    return hasher.transform(data[field])


def add_hash_fields_from_saved_hashes(data):
    for field, num_features in get_hashing_info().items():
        matrix = get_matrix_from_saved_hash(data, field)
        data = add_hashed_matrix_to_data(matrix, data, field, num_features)

    return data


def get_scaler(data):
    return StandardScaler(with_std=True).fit(data)


# SCALER
def scale(data, scaler=None):
    """
    :param data: Dataframe
    :param scaler: a optional scaler, if not provided will fit one.
    :return: scaled data
    """
    fields = list(data)

    if scaler is None:
        scaler = get_scaler(data)

    # At this point 'data' output is not a DataFrame, unfortunately
    data = scaler.transform(data)

    data = pd.DataFrame(data, columns=fields)
    return data


def get_scaler_and_save(data, fields=None):
    scaler = get_scaler(data)
    pickle_handler.save_scaler(scaler, fields)


def scale_data_from_saved_scaler(data, fields=None):
    scaler = pickle_handler.load_scaler(fields)
    return scale(data, scaler=scaler)


def predict_property(candidates, model, selected_fields=None):
    """
    Generic method to predict any property the model (second input) can do.
    :param candidates: Can be either a list of candidates or a single candidate.
    :param model: Any model implementing the sklearn interface.
    :param selected_fields: optional array of fields to select from the data.
    :return: None
    """

    if isinstance(candidates, Candidate):
        candidates = [candidates]

    if not len(candidates):
        return [], []

    data = load_raw_data(candidates)
    data = fill_missing_values(data, defaults=pickle_handler.load_defaults())
    data = add_hash_fields_from_saved_hashes(data)
    data = filter_fields(data, selected_fields)
    data = scale_data_from_saved_scaler(data, fields=selected_fields)

    return model.predict(data), candidates
