import re
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

from beta_invite.models import User


"""Runs machine learning models to try to predict the User characteristics."""
from sklearn.naive_bayes import MultinomialNB
from beta_invite.models import User
from django.db.models import Case, When
#from subscribe import search_engine
from subscribe.cts import *
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from collections import OrderedDict


def get_text_corpus(path, toy=False):

    if not toy:
        text_dict = {int(os.path.basename(p)):
                     open(os.path.join(path, p, os.path.basename(p) + '.txt'), encoding='UTF-8').read()
                     for p in os.listdir(path) if os.path.isdir(os.path.join(path, p))}
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

    print(text_corpus_dict)

    target_dict = get_target_data([user_id for user_id in text_corpus_dict.keys()])

    input_dict = OrderedDict([(user_id, text) for user_id, text in text_corpus_dict.items() if user_id in target_dict.keys()])

    data_counts = count_vectorizer.fit_transform([e for e in input_dict.values()])
    tf_transformer = TfidfTransformer(use_idf=True).fit(data_counts)

    data_tf_idf = tf_transformer.transform(data_counts)
    vocabulary = count_vectorizer.vocabulary_

    return data_tf_idf, vocabulary, input_dict, target_dict


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


def main():

    data_tf_idf, vocabulary, input_dict, target_data = get_text_stats(RESUMES_PATH)

    print('TF_IDF: ' + str(data_tf_idf))
    print('VOCABULARY: ' + str(vocabulary))
    print('INPUT DICT: ' + str(input_dict))
    print('TARGET DATA: ' + str(target_data))

    clf = MultinomialNB().fit(data_tf_idf, [e for e in target_data.values()])


    """
    docs_new = ['God is love', 'OpenGL on the GPU is fast']
    X_new_counts = count_vect.transform(docs_new)
    X_new_tfidf = tfidf_transformer.transform(X_new_counts)

    predicted = clf.predict(X_new_tfidf)

    for doc, category in zip(docs_new, predicted):
        print('%r => %s' % (doc, twenty_train.target_names[category]))
    """


if __name__ == '__main__':
    main()
