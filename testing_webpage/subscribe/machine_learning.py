from sklearn.naive_bayes import MultinomialNB
import search_engine
from cts import *




if __name__ == 'main':
    get_text_stats(path)

    clf = MultinomialNB().fit(X_train_tfidf, twenty_train.target)

    docs_new = ['God is love', 'OpenGL on the GPU is fast']
    X_new_counts = count_vect.transform(docs_new)
    X_new_tfidf = tfidf_transformer.transform(X_new_counts)

    predicted = clf.predict(X_new_tfidf)

    for doc, category in zip(docs_new, predicted):
        print('%r => %s' % (doc, twenty_train.target_names[category]))
