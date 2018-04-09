import statistics
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import VarianceThreshold

from match import common_learning
from subscribe import helper as h
from dashboard.models import Candidate


CANDIDATE_CLUSTER_FILENAME = 'candidate_cluster_model.p'
#SELECTED_CLUSTERS = [1, 2, 3]
SELECTED_CLUSTERS = [0, 2, 3]


# Variables selected according to current business need
SELECTED_FIELDS = ['country_match', 'city_match', 'profession_match', 'min_education']


def get_hashing_info():
    """
    Add new hashing fields here.
    :return: a hashing dict, with key=field_name, value=num_features
    """
    hashing_info = dict()
    hashing_info['campaign'] = 1
    hashing_info['candidate_country'] = 1
    hashing_info['candidate_city'] = 1
    hashing_info['campaign_country'] = 1
    hashing_info['campaign_city'] = 1
    hashing_info['profession'] = 1
    hashing_info['campaign_profession'] = 1
    # TODO: ADD NEW FIELD HERE

    return hashing_info


def predict_cluster(candidates):
    """
    Given candidates predict their cluster.
    :param candidates: Can be either a list of candidates or a single candidate.
    :return: None
    """

    cluster_model = common_learning.load_object(CANDIDATE_CLUSTER_FILENAME)
    return common_learning.predict_property(candidates, cluster_model)#, selected_fields=SELECTED_FIELDS)


def get_std_deviation_per_field(clusters_dict):
    std_dict = dict()
    for field in clusters_dict[0].keys():
        field_values = [my_cluster_dict[field] for cluster_num, my_cluster_dict in clusters_dict.items()]
        std_dict[field] = statistics.stdev(field_values)

    return std_dict


def run():

    #sys.stdout = h.Unbuffered(open('clustering.log', 'a'))

    data, candidates = common_learning.load_data(hashing_info=common_learning.get_hashing_info(),)
                                                 #selected_fields=SELECTED_FIELDS)

    fields = list(data)

    kmeans = KMeans(n_clusters=5, random_state=0).fit(data)
    common_learning.save_object(kmeans, CANDIDATE_CLUSTER_FILENAME)

    clusters_dict = dict()
    for cluster_num, center in enumerate(kmeans.cluster_centers_):
        clusters_dict[cluster_num] = dict()
        for field_num, field in enumerate(fields):
            clusters_dict[cluster_num][field] = center[field_num]

    print(clusters_dict)

    std_dict = get_std_deviation_per_field(clusters_dict)
    print(std_dict)

    selected_clusters = []
    for cluster_num, cluster in clusters_dict.items():
        tuples = [(field, value) for field, value in cluster.items()]

        tuples = reversed(sorted(tuples, key=lambda t: std_dict[t[0]]))
        tuples = [x for x in tuples]
        print(tuples)
        score = sum([score for field, score in tuples])
        if score > 0:
            selected_clusters.append(cluster_num)

    print(selected_clusters)

    for c in predict_cluster(candidates)[0]:
        print(c)

    #print([(p, c) for p, c in zip(predict_cluster(candidates))])


# TODO: use variable importance to cluster and feed classifier, importances are (desc sort):
"""
[('campaign_0', 0.23249602806506706),
('median_test_passed', 0.22608969561168446),
('text_match', 0.15287676893853019),
('campaign_profession_0', 0.090361522775744982),
('campaign_education', 0.058015226675120379),
('education_match', 0.050670652091758847),
('profession_0', 0.045705723250406616),
('education', 0.043930943960110547),
('profession_match', 0.031846130490812412),
('country_match', 0.028050331591441657),
('min_education', 0.013056161568084104),
('candidate_city_0', 0.012410353415412065),
('candidate_country_0', 0.008531106861831339),
('campaign_country_0', 0.0053400402957933298),
('campaign_city_0', 0.00033534815979503182),
('city_match', 0.00028396624840694646)]
"""
