import sys
import os
from django.core.wsgi import get_wsgi_application


# Environment can use the models as if inside the Django app
sys.path.insert(0, '/'.join(os.getcwd().split('/')[:-1]))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

from match.model import predict_match
from dashboard.models import Candidate, State
import numpy as np

candidates = Candidate.objects.filter(state__in=[State.objects.get(code='WFI'), State.objects.get(code='DI')],
                                      campaign_id=178).order_by('-created_at')

prediction_array = np.array([])
for c in candidates:
    prediction, candidates = predict_match(c)
    print('{}: {}'.format(c, prediction))
    prediction_array = np.append(prediction_array, prediction)

print('percentage who passed: {}'.format(np.mean(prediction_array)))
