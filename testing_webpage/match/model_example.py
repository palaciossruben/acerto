
import sys
import os
from django.core.wsgi import get_wsgi_application


# Environment can use the models as if inside the Django app
sys.path.insert(0, '/'.join(os.getcwd().split('/')[:-1]))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

from match.model import predict_match
from dashboard.models import Candidate
import numpy as np

candidates = Candidate.objects.all().order_by('-created_at')[:1000]

prediction_array = np.array([])
for c in candidates:
    prediction, candidates = predict_match(c)
    print(prediction)
    prediction_array = np.append(prediction_array, prediction)

print('percentage who paased: {}'.format(np.mean(prediction_array)))
