"""
Test hypothesis:
1. ¿Correlation of experience and test is low?:

Yes, just 0.068
"""


import os
from django.core.wsgi import get_wsgi_application

# Environment can use the models as if inside the Django app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

import numpy as np

from dashboard.models import Candidate


candidates = [c for c in Candidate.objects.all() if c.evaluations.all() and c.user.experience]

experience = [c.user.experience for c in candidates]
test_score = [max([e.final_score for e in c.evaluations.all()]) for c in candidates]

print(experience)
print(test_score)
print('number of candidates: ' + str(len(candidates)))
print(np.corrcoef(experience, test_score))
