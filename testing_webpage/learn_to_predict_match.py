"""
Here we are learning how to predict if a candidate is a potential match of a company based on his/her profile (CV)
"""

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
from dashboard.models import Candidate
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


def filter_user_ids(text_corpus_dict, target_dict):
    """
    Filters the user_ids
    Args:
        text_corpus_dict: {user_id: text ...}
        target_dict: {user_id: label ...}
    Returns: Returns the text_corpus_dict, filtered
    """
    return OrderedDict([(user_id, text) for (user_id, text) in text_corpus_dict.items() if user_id in target_dict.keys()])


def get_text_stats(path):
    """
    Gets tf_idf transformed data and the vocabulary
    Args:
        path: The directory of the resumes
    Returns: Tuple containing Sparse Matrix with tf_idf data,  vocabulary dictionary and text_corpus (OrderedDict)
    """
    count_vectorizer = CountVectorizer()
    text_corpus_dict = get_text_corpus(path, toy=False)

    user_ids = [user_id for user_id in text_corpus_dict.keys()]
    target_dict = get_target_data(user_ids)

    text_corpus_dict = filter_user_ids(text_corpus_dict, target_dict)

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

    candidates = Candidate.objects.filter(removed=False)

    tmp_tuples = []
    for c in candidates:
        if c.state is not None and c.user_id in user_ids:
            if c.state.code in {'SR', 'WFT', 'ROT', 'ROI', 'RBC'}:
                tmp_tuples.append((c.user_id, 0))
            elif c.state.code in {'WFI', 'STC', 'GTJ'}:
                tmp_tuples.append((c.user_id, 1))

    return OrderedDict(tmp_tuples)


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


EPOCHS = 3000
BATCH_SIZE = 100


def neural_model(input_dim):

    from keras.models import Sequential
    from keras.layers import Dense

    # Construct a model
    model = Sequential()

    layer = Dense(4, input_dim=input_dim, init='glorot_normal', activation='relu')
    model.add(layer)

    layer2 = Dense(3, init='glorot_normal', activation='sigmoid')
    model.add(layer2)

    layer3 = Dense(1, init='glorot_normal', activation='linear')
    model.add(layer3)

    model.compile(loss='mean_squared_error', optimizer='adam', metrics=['accuracy'])

    return model



"""
def neural_model():

    import numpy as np
    from w2v import train_word2vec
    import tensorflow as tf
    sess = tf.Session()

    from keras.models import Sequential, Model
    from keras.layers import Activation, Dense, Dropout, Embedding, Flatten, Input, Merge, Convolution1D, MaxPooling1D
    from keras import backend as K
    K.set_session(sess)

    np.random.seed(2)

    # Parameters
    # ==================================================
    #
    # Model Variations. See Kim Yoon's Convolutional Neural Networks for
    # Sentence Classification, Section 3 for detail.

    model_variation = 'CNN-non-static'  #  CNN-rand | CNN-non-static | CNN-static
    print('Model variation is %s' % model_variation)

    # Model Hyperparameters
    sequence_length = 45
    embedding_dim = 20
    filter_sizes = (3, 4)
    num_filters = 128
    dropout_prob = (0.25, 0.5)
    hidden_dims = 128

    # Training parameters
    batch_size = 32
    num_epochs = 30
    val_split = 0.1

    # Word2Vec parameters, see train_word2vec
    min_word_count = 1  # Minimum word count
    context = 10        # Context window size

    # Data Preparation
    # ==================================================
    #
    # Load data
    #x, y, vocabulary, vocabulary_inv = data_helpers.load_data()

    if model_variation == 'CNN-non-static' or model_variation == 'CNN-static':
        embedding_weights = train_word2vec(x, vocabulary_inv, embedding_dim, min_word_count, context)
        if model_variation == 'CNN-static':
            x = embedding_weights[0][x]
    elif model_variation == 'CNN-rand':
        embedding_weights = None
    else:
        raise ValueError('Unknown model variation')

    # Shuffle data
    shuffle_indices = np.random.permutation(np.arange(len(y)))
    x_shuffled = x[shuffle_indices]
    y_shuffled = y[shuffle_indices].argmax(axis=1)

    print("Vocabulary Size: {:d}".format(len(vocabulary)))

    # Building model
    # ==================================================
    #
    # graph subnet with one input and one output,
    # convolutional layers concatenated in parallel
    graph_in = Input(shape=(sequence_length, embedding_dim))
    convs = []
    for fsz in filter_sizes:
        conv = Convolution1D(nb_filter=num_filters,
                             filter_length=fsz,
                             border_mode='valid',
                             activation='relu',
                             subsample_length=1)(graph_in)
        pool = MaxPooling1D(pool_length=2)(conv)
        flatten = Flatten()(pool)
        convs.append(flatten)

    if len(filter_sizes) > 1:
        out = Merge(mode='concat')(convs)
    else:
        out = convs[0]

    graph = Model(input=graph_in, output=out)

    # main sequential model
    model = Sequential()
    if not model_variation == 'CNN-static':
        model.add(Embedding(len(vocabulary), embedding_dim, input_length=sequence_length,
                            weights=embedding_weights))

    model.add(Dropout(dropout_prob[0], input_shape=(sequence_length, embedding_dim)))
    model.add(graph)
    model.add(Dense(hidden_dims))
    model.add(Dropout(dropout_prob[1]))
    model.add(Activation('relu'))
    model.add(Dense(1))
    model.add(Activation('sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy'])

    # Training model
    # ==================================================
    model.fit(x_shuffled, y_shuffled, batch_size=batch_size,
              nb_epoch=num_epochs, validation_split=val_split, verbose=1)

    model.save('save_tmp.h5')
"""


def reduce_dimensionality(train_set, test_set):
    """
    DIMENSIONALITY REDUCTION:
    Args:
        train_set: set with train
        test_set: set with test
    Returns: Tuple with train and test set with dimension reduced.
    """
    print('REDUCING DIMENSIONALITY')
    from sklearn.decomposition import TruncatedSVD

    svd = TruncatedSVD(n_components=100, n_iter=7, random_state=42)
    svd.fit(train_set)
    print('SVD SUM: ' + str(svd.explained_variance_ratio_.sum()))

    train_set = svd.transform(train_set)
    test_set = svd.transform(test_set)

    return train_set, test_set


def grid_search(model, train_set, train_target):
    """
    Construct model with a search space on the hyper-parameters.
    Args:
        model: any sklearn model
        train_set: input
        train_target: output
    Returns: a model with grid search into it.
    """
    #parameters = {'C': (1e3, 1e4, 1e6, 1e7),
    #              'degree': (1, 2, 3, 4),
    #              }

    #parameters = {'gamma': (10, 1, 0.1, 0.01, 0.001),
    #              'C': (1e3, 1.25e3, 2.5e3),
    #              }

    parameters = {'C': (1e2, 1e3, 1e4),
                  }

    model = GridSearchCV(model, parameters, n_jobs=-1).fit(train_set, train_target)

    print('BEST GRID SEARCH SCORE: ' + str(model.best_score_))
    print('BEST GRID SEARCH PARAMS: ' + str(model.best_params_))

    return model


def rescale_index(target_idx, predicted, targets):
    """
    The arrays "predicted" and "targets" can be different length.
    This is why we have to do a re-scaling
    Args:
        target_idx: A integer with the index of the targets list.
        predicted: list with predicted values.
        targets: list with target values.
    Returns: Target index that corresponds to predicted one.
    """

    predicted_length = len(predicted)
    target_length = len(targets)

    return round(target_idx / target_length * predicted_length)


def get_cutoff_values(predicted, targets):
    """
    The final distribution of values should be the same as the input distribution.
    Based on this idea a re-scaling is done with the distribution percentiles of each class.
    Args:
        predicted: list with predicted values (These are float).
        targets: Integer values the classes.
    Returns: Values which dictate on which final class the prediction is.
    """

    # Sort both lists:
    predicted = sorted(predicted)
    targets = sorted(targets)

    cutoffs = []
    last_value = 0
    for idx, v in enumerate(targets):
        if last_value != v:  # There is a cutoff here.

            # This covers general case when len(predicted) != len(targets)
            predicted_idx = rescale_index(idx, predicted, targets)

            if idx > 0:
                mean = (predicted[predicted_idx] + predicted[predicted_idx-1])/2
            else:
                mean = predicted[predicted_idx]
            cutoffs.append(mean)

        last_value = v

    return cutoffs


def get_value(idx, cutoffs):

    # beyond last value
    if idx > len(cutoffs) - 1:
        return 10000000000
    else:
        return cutoffs[idx]


def cutoff_transform(cutoffs, predicted):

    new_prediction = []
    for p in predicted:
        for idx, c in enumerate(cutoffs):
            if c < p < get_value(idx+1, cutoffs):
                new_prediction.append(idx+1)
                break

            if idx == 0 and p < c:
                new_prediction.append(0)
                break

    return new_prediction


def run_experiment(cutoffs=None):
    """
    Args:
        cutoffs: Optional List with breakpoints for classification, else it will approximate by rounding
    Returns: Arrays for meta-learning
    """

    data_tf_idf, vocabulary, input_dict, target_data, count_vectorizer, tfidf_transformer = get_text_stats('media/resumes')

    #print('TF_IDF: ' + str(data_tf_idf))
    #print('VOCABULARY: ' + str(vocabulary))
    #print('INPUT DICT: ' + str(input_dict))
    #print('TARGET DATA: ' + str(target_data))

    # Fucking sklearn cannot take dictionaries, therefore the OrderedDict is converted to list containing tuples first.
    target_tuple_list = [(k, v) for k, v in target_data.items()]

    data_tf_idf_train, data_tf_idf_test, train_target, test_target = train_test_split(data_tf_idf, target_tuple_list,
                                                                                      test_size=0.3)

    #data_tf_idf_train, data_tf_idf_test = reduce_dimensionality(data_tf_idf_train, data_tf_idf_test)

    #model = neural_model(input_dim=shape(data_tf_idf_train)[1])
    model = SVR(kernel='rbf', C=1e3, gamma=0.001)

    train_target_values = [v for _, v in train_target]
    model.fit(data_tf_idf_train, train_target_values)
    #model.fit(data_tf_idf_train, train_target_values, nb_epoch=EPOCHS, batch_size=BATCH_SIZE)


    # grid_search(model, train_set, train_target)
    # toy_test(count_vectorizer, tfidf_transformer, model)

    train_predicted = model.predict(data_tf_idf_train)

    train_predicted = [int(round(e)) for e in train_predicted]

    print('TRAIN ACCURACY: ' + str(np.mean(train_predicted == train_target_values)))

    test_predicted_float = list(model.predict(data_tf_idf_test))

    if cutoffs is not None:
        test_predicted = cutoff_transform(cutoffs, test_predicted_float)
    else:
        test_predicted = np.array([int(round(e)) for e in test_predicted_float])

    test_target_values = np.array([e for _, e in test_target])
    test_target_keys = np.array([k for k, _ in test_target])
    test_accuracy = np.mean(test_predicted == test_target_values)

    print('TEST USER IDS: ' + str(test_target_keys))
    print('TEST TARGET' + str(test_target_values))
    print('TEST PREDICTION' + str(test_predicted))
    print('TEST ACCURACY: ' + str(test_accuracy))

    train_error_dict = get_errors_dict(train_target, train_predicted)
    test_error_dict = get_errors_dict(test_target, test_predicted)

    return test_accuracy, train_error_dict, test_error_dict, test_predicted_float, train_target_values


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


def make_collective_experiment(num_experiments, cutoffs=None):
    """
    Args:
        num_experiments: Number of iterations.
        cutoffs: ????
    Returns:
    """

    accuracy = np.array([])
    train_error_list = []
    test_error_list = []
    all_train_target = []
    all_test_predicted_float = []
    for _ in range(num_experiments):

        current_accuracy, train_error_dict, test_error_dict, test_predicted_float, train_target_values = run_experiment(cutoffs=cutoffs)

        all_train_target += train_target_values
        all_test_predicted_float += test_predicted_float

        accuracy = np.append(accuracy, current_accuracy)

        train_error_list.append(train_error_dict)
        test_error_list.append(test_error_dict)

    average_test_error = get_avg_error_dict(test_error_list)

    # SORTED ERRORS
    print('AVERAGE TEST ERROR: ' + str(sort_error_dict(average_test_error)))
    print('AVERAGE TEST ACCURACY: ' + str(np.mean(accuracy)))
    print('STD-DEV TEST ACCURACY: ' + str(np.std(accuracy)))

    return all_test_predicted_float, all_train_target


if __name__ == '__main__':

    start_time = time.time()

    all_test_predicted_float, all_train_target = make_collective_experiment(num_experiments=300)

    #cutoffs = get_cutoff_values(all_test_predicted_float, all_train_target)
    #print('CUTOFFS: ' + str(cutoffs))
    #make_collective_experiment(100, cutoffs=cutoffs)

    print("--- %s seconds ---" % (time.time() - start_time))
