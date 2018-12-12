"""
This task updates the last evalution of each candidate
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

# Environment can use the models as if inside the Django app
sys.path.insert(0, '/'.join(os.getcwd().split('/')[:-1]))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

from dashboard.models import Candidate

candidates = Candidate.objects.all()

for c in candidates:
    c.last_evaluation = c.get_last_evaluation()
    c.save()
    print('updated last eval for: {}'.format(c.id))
