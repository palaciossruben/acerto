import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

import pickle
import common

d = pickle.load(open(common.RELATED_WORDS_PATH, 'rb'))

for k, v in d.items():
    print(str(k) + ': ' + str(v))
