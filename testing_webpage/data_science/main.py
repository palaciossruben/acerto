"""
Test hypothesis:
1. Correlación entre puntaje prueba y probabilidad de pasar entrevista.
2. Correlación entre puntaje y tiempo para contestar prueba.
3. Los que contestan muy poco en los open field, así el resto de los test estén súper bien, normalmente han sido rechazados
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


candidates = [c for c in Candidate.objects.all() if c.state.passed_test() and c.evaluations.all()]

passed_interview = [int(c.state.passed_interview()) for c in candidates]
test_score = [max([e.final_score for e in c.evaluations.all()]) for c in candidates]

#passed_interview = np.array([0, 0, 0, 1, 1, 1])
#test_score = [e * 10 + 100 for e in np.arange(6)]
print(passed_interview)
print(test_score)
print('number of candidates: ' + str(len(candidates)))
print('% of people passing interview: ' + str(np.average(passed_interview) * 100))
print(stats.pointbiserialr(passed_interview, test_score))
