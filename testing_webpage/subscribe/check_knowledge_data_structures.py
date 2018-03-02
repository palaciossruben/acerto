import pickle

"""
d = pickle.load(open('relevance_dictionary.p', 'rb'))

for k, v in d.items():
    print(str(k) + ': ' + str(v))


d = pickle.load(open('word_user_dictionary.p', 'rb'))

for k, v in d.items():
    print(str(k) + ': ' + str(v))
"""

d = pickle.load(open('top_related_words_dict.p', 'rb'))

for k, v in d.items():
    print(str(k) + ': ' + str(v))
