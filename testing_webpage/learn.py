"""Runs machine learning models to try to predict the User characteristics."""
import re
import os
import time
import numpy as np

from sklearn.svm import SVR
from django.core.wsgi import get_wsgi_application
from sklearn.model_selection import train_test_split

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

from beta_invite.models import User, Education
from beta_invite.models import User
from django.db.models import Case, When
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from collections import OrderedDict
from sklearn.model_selection import GridSearchCV

def get_text_corpus(path, toy=False):
    """
    Args:
        path: Path to the media files.
        toy: Boolean indicating if a toy data set should be used.
    Returns: Dictionary of the form {id: text}
    """
    if not toy:

        text_dict = {}

        for p in os.listdir(path):
            if os.path.isdir(os.path.join(path, p)):
                try:
                    text = open(os.path.join(path, p, os.path.basename(p) + '.txt'), encoding='UTF-8').read()
                    text_dict[int(os.path.basename(p))] = text
                except FileNotFoundError:
                    # not a big deal file, if no file found.
                    pass

        #text_dict = {int(os.path.basename(p)):
        #             open(os.path.join(path, p, os.path.basename(p) + '.txt'), encoding='UTF-8').read()
        #             for p in os.listdir(path) if os.path.isdir(os.path.join(path, p))}
        text_dict = OrderedDict(text_dict)
    else:
        # Small data set to understand algorithms
        text_dict = OrderedDict({1: 'common juan pedro',
                                 2: 'common camilo',
                                 3: 'common alberto high high high',
                                 4: ''})

    # filter any numbers:
    for user_id, text in text_dict.items():
        # TODO: what about letters number combinations such as 'python3'
        text_dict[user_id] = re.sub(r'\d+', '',  text)

    return text_dict


def get_text_stats(path):
    """
    Gets tf_idf transformed data and the vocabulary
    Args:
        path: The directory of the resumes
    Returns: Tuple containing Sparse Matrix with tf_idf data,  vocabulary dictionary and text_corpus (OrderedDict)
    """
    count_vectorizer = CountVectorizer()
    text_corpus_dict = get_text_corpus(path, toy=False)

    target_dict = get_target_data([user_id for user_id in text_corpus_dict.keys()])

    input_dict = OrderedDict([(user_id, text) for user_id, text in text_corpus_dict.items() if user_id in target_dict.keys()])

    data_counts = count_vectorizer.fit_transform([e for e in input_dict.values()])
    tfidf_transformer = TfidfTransformer(use_idf=True).fit(data_counts)

    data_tf_idf = tfidf_transformer.transform(data_counts)
    vocabulary = count_vectorizer.vocabulary_

    return data_tf_idf, vocabulary, input_dict, target_dict, count_vectorizer, tfidf_transformer


def retrieve_sorted_users(user_ids):
    """
    Gets the objects in the same order of the user_ids list.
    Args:
        user_ids: List of user ids.
    Returns: Sorted User objects Query Set.
    """
    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(user_ids)])
    return User.objects.filter(pk__in=user_ids).order_by(preserved)


def get_target_data(user_ids):
    """
    Args:
        user_ids: List of User ids.
    Returns: User education in the same order of the user ids.
    """
    users = retrieve_sorted_users(user_ids)
    return OrderedDict([(u.id, u.education.level) for u in users if u.education is not None])


def get_education():
    """

    Returns: Dictionary with the {level: name}
    """
    education = Education.objects.all()
    return {e.level: e.name for e in education}


def toy_test(count_vectorizer, tfidf_transformer, clf):

        # Small Manual Tests
    docs_new = ['Juan Camilo secundaria coisas sin sentido oficios varios',
                'Delta force whash tecnico SENA',
                'ruido por aca Ingeniero Mecanico mas ruido Universidad de los andes secundaria lalala lilli',
                'maestria going forward doing forward secundaria',  # wrong: its master
                'universidad maestria going forward doing forward',  # wrong: its master
                'maestria going forward doing forward']

    X_new_counts = count_vectorizer.transform(docs_new)
    X_new_tfidf = tfidf_transformer.transform(X_new_counts)

    predicted = clf.predict(X_new_tfidf)

    education_dict = get_education()

    for doc, level in zip(docs_new, predicted):
        print('%r => %s' % (doc, education_dict[level]))


def get_errors_dict(target, predicted):
    """
    Args:
        target: Dict where key is the User.id and values is the target education level.
        predicted: Ordered List with predictions.
    Returns: OrderDict with error per document.
    """
    return OrderedDict([(k, abs(tag-predicted)) for (k, tag), predicted in zip(target, predicted)])


def main():

    data_tf_idf, vocabulary, input_dict, target_data, count_vectorizer, tfidf_transformer = get_text_stats('media/resumes')

    #print('TF_IDF: ' + str(data_tf_idf))
    #print('VOCABULARY: ' + str(vocabulary))
    #print('INPUT DICT: ' + str(input_dict))
    #print('TARGET DATA: ' + str(target_data))

    #target = [e for e in target_data.values()]

    # Fucking skleanr cannot take dictionaries, therefore the ORder Dict is converted to list containing tuples first.
    target_tuple_list = [(k, v) for k, v in target_data.items()]

    data_tf_idf_train, data_tf_idf_test, train_target, test_target = train_test_split(data_tf_idf, target_tuple_list,
                                                                                      test_size=0.05)

    # DIMENSIONALITY REDUCTION:
    #from sklearn.decomposition import TruncatedSVD

    #svd = TruncatedSVD(n_components=10, n_iter=7, random_state=42)
    #svd.fit(data_tf_idf_train)
    #print('SVD SUM: ' + str(svd.explained_variance_ratio_.sum()))

    #data_tf_idf_train = svd.transform(data_tf_idf_train)
    #data_tf_idf_test = svd.transform(data_tf_idf_test)

    #clf = SGDClassifier(loss='hinge', penalty='l2',
    #                    alpha=1e-4, n_iter=5, random_state=42)

    #clf = SVR(kernel='rbf', C=1e3, gamma=0.001)
    clf = SVR(kernel='rbf', C=1e6, gamma=0.1)
    #svr_lin = SVR(kernel='linear', C=1e3)
    #clf = SVR(kernel='poly', C=1e3, degree=2)

    train_target_values = [v for _, v in train_target]
    clf.fit(data_tf_idf_train, train_target_values)

    #parameters = {#'vect__ngram_range': [(1, 1), (1, 2)],
    #              #'tfidf__use_idf': (True, False),
    #              'alpha': (10, 1, 1e-1, 1e-2, 1e-3, 1e-4),
    #}

    #parameters = {'gamma': (10, 1, 0.1, 0.01, 0.001),
    #              'C': (1e3, 1.25e3, 2.5e3),
    #              }

    #clf = GridSearchCV(clf, parameters, n_jobs=-1).fit(data_tf_idf_train, train_target_values)

    #print(clf.best_score_)
    #print(clf.best_params_)

    # {'C': 1000.0, 'gamma': 0.001} {'C': 10000.0, 'gamma': 0.001}

    # toy_test(count_vectorizer, tfidf_transformer, clf)

    train_predicted = clf.predict(data_tf_idf_train)
    train_predicted = [int(round(e)) for e in train_predicted]
    print('TRAIN ACCURACY: ' + str(np.mean(train_predicted == train_target_values)))

    test_predicted = clf.predict(data_tf_idf_test)
    test_predicted = np.array([int(round(e)) for e in test_predicted])
    test_target_values = np.array([e for _, e in test_target])
    test_target_keys = np.array([k for k, _ in test_target])
    test_accuracy = np.mean(test_predicted == test_target_values)

    print('TEST USER IDS: ' + str(test_target_keys))
    print('TEST TARGET' + str(test_target_values))
    print('TEST PREDICTION' + str(test_predicted))
    print('TEST ACCURACY: ' + str(test_accuracy))

    train_error_dict = get_errors_dict(train_target, train_predicted)
    test_error_dict = get_errors_dict(test_target, test_predicted)

    return test_accuracy, train_error_dict, test_error_dict


def get_avg_error_dict(error_list):
    """
    Returns Dictionary with avg error per User.id
    Args:
        error_list: A list containing dictionaries, each one of them has the error for particular User.id
    Returns: Dictionary with User.id as key and value a tuple having average error and number of observations.
        The avg error for each User.id. This can aid in finding particular weaknesses on the whole classification
        pipeline.
    """

    avg_error_dict = {}
    for d in error_list:
        for k, error in d.items():
            if avg_error_dict.get(k) is None:
                avg_error_dict[k] = (error, 1)
            else:
                avg_error, num_observations = avg_error_dict[k]

                # Here uses Weighted avg formula
                new_avg_error = (avg_error*num_observations + error)/(num_observations + 1)
                avg_error_dict[k] = (new_avg_error, num_observations + 1)

    return avg_error_dict


def sort_error_dict(average_error):
    return sorted([(k, v) for k, v in average_error.items()], key=lambda x: -x[1][0])


if __name__ == '__main__':

    start_time = time.time()

    num_experiments = 500
    accuracy = np.array([])
    train_error_list = []
    test_error_list = []
    for _ in range(num_experiments):

        current_accuracy, train_error_dict, test_error_dict = main()

        accuracy = np.append(accuracy, current_accuracy)

        train_error_list.append(train_error_dict)
        test_error_list.append(test_error_dict)

    average_train_error = get_avg_error_dict(train_error_list)
    average_test_error = get_avg_error_dict(test_error_list)

    # SORTED ERRORS
    #print('AVERAGE TRAIN ERROR: ' + str(sort_error_dict(average_train_error)))
    print('AVERAGE TEST ERROR: ' + str(sort_error_dict(average_test_error)))

    print('AVERAGE TEST ACCURACY: ' + str(np.mean(accuracy)))
    print('STD-DEV TEST ACCURACY: ' + str(np.std(accuracy)))

    print("--- %s seconds ---" % (time.time() - start_time))
