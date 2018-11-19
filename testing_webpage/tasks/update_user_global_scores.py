"""
This task updates the global scores of the users
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

# Environment can use the models as if inside the Django app
sys.path.insert(0, '/'.join(os.getcwd().split('/')[:-1]))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

import common
from beta_invite.models import User


users = User.objects.all()

for u in users:
    common.update_scores_of_user(u)
    print('updated scores from user_id: {}'.format(u.id))


for u in users:
    print('for user_id: {}'.format(u.id))
    print('scores = {}'.format(list(u.scores.all())))
