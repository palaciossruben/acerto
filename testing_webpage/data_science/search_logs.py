import os
from django.core.wsgi import get_wsgi_application
import sys

# Environment can use the models as if inside the Django app
if 'win' in sys.platform:
    sys.path.insert(0, '\\'.join(os.getcwd().split('\\')[:-1]))
else:
    sys.path.insert(0, '/'.join(os.getcwd().split('/')[:-1]))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

from beta_invite.models import SearchLog

search_logs = SearchLog.objects.all()

#for s in search_logs:
#    print(s)

# Last campaign
last_search = SearchLog.objects.all().order_by('-created_at').first()
print(last_search)

