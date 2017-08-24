import os
from datetime import datetime, timedelta
from django.core.wsgi import get_wsgi_application

# Environment can use the models as if inside the Django app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

from beta_invite.models import User
from beta_invite.util import email_sender

users = User.objects.filter(created_at__range=[str(datetime.now() - timedelta(days=1)), str(datetime.now())])


email_sender.send_daily_report(language_code='es',
                               body_filename='daily_report_email_body',
                               subject='Daily report',
                               recipient='juan@peaku.co',
                               users=users)
