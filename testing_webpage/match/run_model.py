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

import time
import pickle
from datetime import datetime

from match import common_learning, learn, text_match


def load_data_for_prediction():
    """
    Loads and prepares all data.
    :return: data DataFrame with features and target.
    """
    data, candidates = common_learning.load_data()
    print('PERCENTAGE OF NULL BY COLUMN: ' + str(common_learning.get_nan_percentages(data)))
    return common_learning.fill_missing_values(data), candidates


def predict_and_save(data, model, candidates):

    data['prediction'] = model.predict(data)

    for candidate, (pk, row) in zip(candidates, data.iterrows()):
        candidate.match = row['prediction']
        candidate.save()


def learn_and_predict():
    """
    Predict matches ans stores them on the candidates.
    :return: None
    """
    # TODO: load model, when getting new candidate
    #model = pickle.load(open("match/model.p", "rb"))
    model, _ = learn.get_model()
    pickle.dump(model, open("model.p", "wb"))

    data, candidates = load_data_for_prediction()
    predict_and_save(data, model, candidates)


if __name__ == '__main__':
    t0 = time.time()
    text_match.update()
    learn_and_predict()
    t1 = time.time()
    print('On {0} LEARN AND PREDICT_MATCH, took: {1}'.format(datetime.today(), t1 - t0))
