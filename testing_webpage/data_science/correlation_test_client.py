"""
Test hypothesis:
1. ¿Correlation of tests and client decision is high?:

"""


import os
from django.core.wsgi import get_wsgi_application

# Environment can use the models as if inside the Django app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

from scipy import stats
import numpy as np

from dashboard.models import Candidate


candidates = [c for c in Candidate.objects.all() if c.state.passed_interview() and c.evaluations.all()]

passed_interview = [int(c.state.looks_good()) for c in candidates]
test_score = [max([e.final_score for e in c.evaluations.all()]) for c in candidates]

print(passed_interview)
print(test_score)
print('number of candidates: ' + str(len(candidates)))
print('% of people passing interview: ' + str(np.average(passed_interview) * 100))
print(stats.pointbiserialr(passed_interview, test_score))


