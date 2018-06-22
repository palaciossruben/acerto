import pickle

d = pickle.load(open('related_words_dict.p', 'rb'))

for k, v in d.items():
    try:
        print(str(k) + ': ' + str(v))
    except UnicodeEncodeError:
        pass
