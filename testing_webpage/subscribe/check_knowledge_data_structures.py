import pickle
from subscribe import cts as cts_subscribe

d = pickle.load(open(cts_subscribe.RELATED_WORDS_PATH, 'rb'))

for k, v in d.items():
    print(str(k) + ': ' + str(v))
