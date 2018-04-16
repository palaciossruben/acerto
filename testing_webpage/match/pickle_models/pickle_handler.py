"""
Handles the pickling of any model
"""
import os
import pickle

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
CANDIDATE_CLUSTER = 'candidate_cluster_model.p'
DEFAULTS = 'defaults.p'
REGRESSION_MODEL = 'regression_model.p'
CLASSIFIER = 'classifier.p'
REGRESSION = 'regression.p'
HASHER = 'hasher_{}.p'
SCALER = 'scaler.p'
SCALER_FIELDS = 'scaler_{}.p'
SELECTED_CLUSTERS = 'selected_clusters.p'


def get_path(file_name):
    return os.path.join(DIR_PATH, file_name)


def save_object(my_object, filename):
    pickle.dump(my_object, open(get_path(filename), "wb"))


def load_object(filename):
    return pickle.load(open(get_path(filename), "rb"))


# SCALER

def get_scaler_name_with_fields(fields=None):
    """
    :param fields: Optional list of fields, for having a scaler only on those fields.
    :return: str
    """
    if fields is None:
        return SCALER
    else:
        return SCALER_FIELDS.format(fields)


def load_scaler(fields):
    return load_object(get_scaler_name_with_fields(fields=fields))


def save_scaler(scaler, fields):
    save_object(scaler, get_scaler_name_with_fields(fields=fields))


# DEFAULTS

def save_defaults(defaults):
    save_object(defaults, DEFAULTS)


def load_defaults():
    return load_object(DEFAULTS)


# CLUSTER

def save_cluster(cluster):
    save_object(cluster, CANDIDATE_CLUSTER)


def load_cluster():
    return load_object(CANDIDATE_CLUSTER)


def save_selected_clusters(cluster):
    save_object(cluster, SELECTED_CLUSTERS)


def load_selected_clusters():
    return load_object(SELECTED_CLUSTERS)


# HASHER

def get_hasher_name(field):
    return HASHER.format(field)


def load_hasher(field):
    return load_object(get_hasher_name(field))


def save_hasher(hasher, field):
    save_object(hasher, get_hasher_name(field))


# MODEL

def save_model(regression, model):
    if regression:
        save_object(model, REGRESSION)
    else:
        save_object(model, CLASSIFIER)


def load_model(regression=True):
    if regression:
        return load_object(REGRESSION)
    else:
        return load_object(CLASSIFIER)
