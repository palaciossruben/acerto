import pickle

d = pickle.load(open('word_user_dictionary.p', 'rb'))

for idx, (k, v) in enumerate(d.items()):
    if idx > 100:
        break
    try:
        print(str(k) + ': ' + str(v))
    except UnicodeEncodeError:
        pass
