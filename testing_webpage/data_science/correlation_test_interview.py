"""
Test hypothesis:
1. Correlation of tests with interview-client:

For last technical campaigns:
correlation = 0.39
% of people accepted by client = 33%

For campaigns before that:
correlation = 0.022
% of people accepted by client = 23%

2. Correlación entre puntaje y tiempo para contestar prueba.
3. Correlation between number of words in open fields and passing the interview, despite passing test
4. El mejor test predictivo de rendimiento es el cognitivo
"""


import os
from django.core.wsgi import get_wsgi_application

# Environment can use the models as if inside the Django app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

from scipy import stats
import numpy as np

from dashboard.models import Candidate


last_technical_campaign_ids = [87, 80, 86, 76, ]
candidates = [c for c in Candidate.objects.all() if c.state.passed_test() and c.evaluations.all() and
              c.campaign.pk not in last_technical_campaign_ids]

passed_interview = [int(c.state.looks_good()) for c in candidates]
test_score = [max([e.final_score for e in c.evaluations.all()]) for c in candidates]

print(passed_interview)
print(test_score)
print('number of candidates: ' + str(len(candidates)))
print('% of people passing interview: ' + str(np.average(passed_interview) * 100))
print(stats.pointbiserialr(passed_interview, test_score))


