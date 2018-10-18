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
    #hashing_info['candidate_country'] = 1
    #hashing_info['candidate_city'] = 1
    #hashing_info['campaign_country'] = 1
    #hashing_info['campaign_city'] = 1
    #hashing_info['profession'] = 1
    #hashing_info['campaign_profession'] = 3
    #hashing_info['gender'] = 1
    #hashing_info['candidate_work_area'] = 1
    #hashing_info['neighborhood'] = 1
    #hashing_info['languages'] = 1
    #hashing_info['dream_job'] = 1
    #hashing_info['campaign_work_area'] = 1

    # TODO: ADD NEW FIELD HERE

    # TODO: different hashes for the same property, eg: candidate country and campaign country
    return hashing_info


def hash_columns(data, hashing_info):
    for field, num_features in hashing_info.items():
        data = hash_column(data, field, num_features)

    return data


def get_filtered_candidates():
    """Very good candidates contrasted with very bad ones"""
    return Candidate.objects.exclude(campaign_id__in=[constants.DEFAULT_CAMPAIGN_ID])\
        .filter(state__in=State.get_recommended_states() + State.get_rejected_states())


"""
# TODO add new fields
    programs = models.CharField(max_length=250, null=True)
    address = models.CharField(max_length=100, null=True)
    profile = models.CharField(max_length=250, null=True)
    phone2 = models.CharField(max_length=40, null=True)
    phone3 = models.CharField(max_length=40, null=True)
    document = models.CharField(max_length=50, null=True)
    hobbies = models.CharField(max_length=250, null=True)
"""


def get_columns():
    return [#'campaign',
            #'id',
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
            'candidate_work_area',
            # TODO: had only None, can add later on with more data
            'salary',
            #'neighborhood',
            #'languages',
            #'dream_job',
            'campaign_work_area',
            'has_photo',
            'has_profile',
            'has_twitter',
            'has_facebook',
            'has_instagram',
            'has_linkedin',
            'has_brochure_url',
            'campaign_salary_low',
            'campaign_salary_high',
            ]


def from_list_to_query_set(candidates):
    """Efficiency reasons... do 1 query instead of thousands, later on"""
    return Candidate.objects.filter(pk__in=[c.pk for c in candidates])


def lower_str(text):
    if isinstance(text, str):
        return text.lower()
    else:
        return text


def get_test_column_name(test):
    return str(test.id) + '_' + common.remove_accents(test.name).lower()


def get_salary_match(data):
    """
    I candidate in a soft salary range?
    :param data:
    :return:
    """
    avg = (data['campaign_salary_high'] + data['campaign_salary_low']) / 2
    added_range = avg * 0.25
    soft_high = data['campaign_salary_high'] + added_range
    soft_low = data['campaign_salary_low'] - added_range

    df_tmp = pd.DataFrame([data['salary'], soft_high, soft_low], columns=['salary', 'soft_high', 'soft_low'])

    return df_tmp.apply(lambda row: row['soft_low'] <= row['salary'] <= row['soft_high'], axis=1)


def add_synthetic_fields(data):
    """Calculated fields"""

    data.loc[:, 'country_match'] = data['candidate_country'] == data['campaign_country']
    data.loc[:, 'city_match'] = data['candidate_city'] == data['campaign_city']
    data.loc[:, 'profession_match'] = data['campaign_profession'] == data['profession']
    data.loc[:, 'education_match'] = data['campaign_education'] == data['education']
    data.loc[:, 'min_education'] = data['campaign_education'] <= data['education']
    data.loc[:, 'work_area_match'] = data['campaign_work_area'] == data['candidate_work_area']
    #data['salary_match'] = get_salary_match(data)
    data.loc[:, 'test_delta'] = data['last_test_score'] - data['last_cut_score']

    return data


def has_url(data, field):
    data.loc[:, field] = data[field].apply(lambda x: 1 if isinstance(x, str) and x != '#' else 0)
    return data


def load_raw_data(candidates=get_filtered_candidates()):

    if isinstance(candidates, list):
        candidates = from_list_to_query_set(candidates)

    # With QuerySet it is much faster.
    data_list = list(candidates.values_list(#'campaign_id',
                                            #'id',  # only to trace the candidate
                                            'text_match',
                                            'user__country_id',
                                            'user__city_id',
                                            'campaign__country_id',
                                            'campaign__city__id',
                                            'user__profession_id',
                                            'campaign__profession_id',
                                            'user__education__level',
                                            'campaign__education__level',
                                            'user__gender_id',
                                            'user__work_area_id',
                                            'user__salary',
                                            #'user__neighborhood',  # TODO: improve input
                                            #'user__languages',  # TODO: improve input
                                            #'user__dream_job',  # TODO: improve input
                                            'campaign__work_area_id',
                                            'user__photo_url',
                                            'user__profile',
                                            'user__twitter',
                                            'user__facebook',
                                            'user__instagram',
                                            'user__linkedin',
                                            'user__brochure_url',
                                            'campaign__salary_low_range',
                                            'campaign__salary_high_range',

                                            # TODO: ADD NEW FIELD HERE
                                            ))

    data = pd.DataFrame(data_list, columns=get_columns(), index=[c.id for c in candidates])

    # Pre-Processing
    #data['neighborhood'] = [lower_str(common.remove_accents(n)) for n in data['neighborhood']]
    #data['languages'] = [lower_str(common.remove_accents(n)) for n in data['languages']]
    #data['dream_job'] = [lower_str(common.remove_accents(n)) for n in data['dream_job']]
    data = has_url(data, 'has_photo')
    data.loc[:, 'has_profile'] = data['has_profile'].apply(lambda x: 1 if isinstance(x, str) and len(x) > 50 else 0)  # more tan 50 chars
    data = has_url(data, 'has_twitter')
    data = has_url(data, 'has_facebook')
    data = has_url(data, 'has_instagram')
    data = has_url(data, 'has_linkedin')
    data = has_url(data, 'has_brochure_url')

    # similar accuracy with high and low complexity:
    data.loc[:, 'last_test_score'] = [c.get_last_score() for c in candidates]
    data.loc[:, 'last_cut_score'] = [c.get_last_cut_score() for c in candidates]

    data.loc[:, 'cognitive_score'] = [c.get_last_cognitive_score() for c in candidates]
    data.loc[:, 'technical_score'] = [c.get_last_technical_score() for c in candidates]
    data.loc[:, 'requirements_score'] = [c.get_last_requirements_score() for c in candidates]
    data.loc[:, 'motivation_score'] = [c.get_last_motivation_score() for c in candidates]
    data.loc[:, 'cultural_fit_score'] = [c.get_last_cultural_fit_score() for c in candidates]

    # Dirty code: INDIVIDUAL TESTS
    # TODO: currently not giving any significant improvement
    """
    test_columns = set()
    for c in candidates.all():
        c.update_mean_test_scores()
        test_columns |= {get_test_column_name(s.test) for s in c.mean_scores.all()}

    # Fill columns with nan first
    for column in test_columns:
        data[column] = np.nan

    data.set_index('id', inplace=True)
    for c in candidates.all():
        for s in c.mean_scores.all():
            data.loc[c.id, get_test_column_name(s.test)] = s.value
    data.reset_index(inplace=True)
    data.drop('id', inplace=True, axis=1)

    for column in test_columns:
        data[column].fillna(np.nanmedian(data[column]), inplace=True)

    for column in test_columns:
        if statistics.stdev(list(data[column])) < 3:
            data.drop(column, inplace=True, axis=1)
            print('dropped column: ' + column)
    """

    return data


def load_data(candidates=get_filtered_candidates(), hashing_info=get_hashing_info()):
    """
    Loads and prepares all data.
    :return: data DataFrame with features and target + candidates.
    """
    data = load_raw_data(candidates)
    data = fill_missing_values(data)
    data = add_synthetic_fields(data)
    #data = hash_columns(data, hashing_info)

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

    #defaults['campaign'] = right_mode(data['campaign'])
    #defaults['id'] = right_mode(data['id'])
    defaults['last_test_score'] = np.nanmedian(data['last_test_score'])
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
    defaults['candidate_work_area'] = right_mode(data['candidate_work_area'])
    #defaults['neighborhood'] = right_mode(data['neighborhood'])
    #defaults['languages'] = right_mode(data['languages'])
    #defaults['dream_job'] = right_mode(data['dream_job'])
    defaults['campaign_work_area'] = right_mode(data['campaign_work_area'])
    defaults['cognitive_score'] = np.nanmedian(data['cognitive_score'])
    defaults['technical_score'] = np.nanmedian(data['technical_score'])
    defaults['requirements_score'] = np.nanmedian(data['requirements_score'])
    defaults['motivation_score'] = np.nanmedian(data['motivation_score'])
    defaults['cultural_fit_score'] = np.nanmedian(data['cultural_fit_score'])
    defaults['has_photo'] = right_mode(data['has_photo'])
    defaults['has_profile'] = right_mode(data['has_profile'])
    defaults['has_twitter'] = right_mode(data['has_twitter'])
    defaults['has_facebook'] = right_mode(data['has_facebook'])
    defaults['has_instagram'] = right_mode(data['has_instagram'])
    defaults['has_linkedin'] = right_mode(data['has_linkedin'])
    defaults['has_brochure_url'] = right_mode(data['has_brochure_url'])
    defaults['campaign_salary_low'] = np.nanmedian(data['campaign_salary_low'])
    defaults['campaign_salary_high'] = np.nanmedian(data['campaign_salary_high'])
    defaults['salary'] = np.nanmedian(data['salary'])
    defaults['last_cut_score'] = np.nanmedian(data['last_cut_score'])

    # TODO: ADD NEW FIELD HERE

    for column in data.columns.values:
        if 'test' in column:
            defaults[column] = np.nanmedian(data[column])

    return defaults


def fill_missing_values(data, defaults=None):

    if defaults is None:
        defaults = calculate_defaults(data)

    for column in list(data):
        data.loc[:, column] = data[column].fillna(defaults[column])

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


def predict_property(candidates, model):
    """
    Generic method to predict any property the model (second input) can do.
    :param candidates: Can be either a list of candidates or a single candidate.
    :param model: Any model implementing the sklearn interface.
    :return: None
    """

    if isinstance(candidates, Candidate):
        candidates = [candidates]

    if not len(candidates):
        return [], []

    data = load_raw_data(candidates)
    data = fill_missing_values(data, defaults=pickle_handler.load_defaults())
    data = add_synthetic_fields(data)
    #data = add_hash_fields_from_saved_hashes(data)  # TODO: removed due to a bug on sklearn hash library, small vectors give different values than big ones
    #data = scale_data_from_saved_scaler(data)

    return model.predict(data), candidates
