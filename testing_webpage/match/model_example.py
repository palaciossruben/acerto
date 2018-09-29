from match.model import predict_match
from dashboard.models import Candidate
import numpy as np
import pandas as pd
from match.pickle_models import pickle_handler


def make_column_hashable(data, column_name):
    if not isinstance(data.loc[0, column_name], str):
        data[column_name] = data[column_name].apply(lambda x: str(x))
    return data


def get_matrix_from_saved_hash(data, field):
    data = make_column_hashable(data, field)
    hasher = pickle_handler.load_hasher(field)
    return hasher.transform(data[field])


candidates = Candidate.objects.all().order_by('-created_at')[:1000]

prediction_array = np.array([])
for c in candidates:
    prediction, candidates = predict_match(c)
    print(prediction)
    prediction_array = np.append(prediction_array, prediction)

print(np.mean(prediction_array))

print(candidates)


"""
data = pd.DataFrame([2, 2, 15], columns=['campaign_city'])

out = get_matrix_from_saved_hash(data, 'campaign_city')
print(out)


data = pd.DataFrame([2, 2], columns=['campaign_city'])

out = get_matrix_from_saved_hash(data, 'campaign_city')
print(out)
"""
