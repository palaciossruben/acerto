import statistics
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import VarianceThreshold

from match import common_learning


def get_hashing_info():
    """
    Add new hashing fields here.
    :return: a hashing dict, with key=field_name, value=num_features
    """
    hashing_info = dict()
    hashing_info['profession'] = 1
    hashing_info['campaign'] = 1
    hashing_info['candidate_country'] = 1
    hashing_info['candidate_city'] = 1
    hashing_info['campaign_country'] = 1
    hashing_info['campaign_city'] = 1
    # TODO: ADD NEW FIELD HERE

    return hashing_info


data, candidates = common_learning.load_data(hashing_info=get_hashing_info())

data = data.loc[:, (data != data.iloc[0]).any()]

data.drop(['min_test_passed',
           'mean_test_passed',
           'max_test_passed',
           'mean_test_final_score',
           'median_test_final_score',
           'min_test_final_score',
           'max_test_final_score'], inplace=True, axis=1)


fields = list(data)

scaler = StandardScaler(with_std=True)
scaler.fit(data)
data = scaler.transform(data)
#selector = VarianceThreshold()
#data = selector.fit_transform(data)

kmeans = KMeans(n_clusters=3, random_state=0).fit(data)

clusters_dict = dict()
for cluster_num, center in enumerate(kmeans.cluster_centers_):
    clusters_dict[cluster_num] = dict()
    for field_num, field in enumerate(fields):
        clusters_dict[cluster_num][field] = center[field_num]

print(clusters_dict)


std_dict = dict()
for field in clusters_dict[0].keys():
    field_values = [my_cluster_dict[field] for cluster_num, my_cluster_dict in clusters_dict.items()]
    std_dict[field] = statistics.stdev(field_values)

print(std_dict)

for cluster in clusters_dict.values():
    tuples = [(field, value) for field, value in cluster.items()]

    tuples = reversed(sorted(tuples, key=lambda t: std_dict[t[0]]))

    print([x for x in tuples])

