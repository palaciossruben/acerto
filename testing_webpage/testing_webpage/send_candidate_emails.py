import os
from django.core.wsgi import get_wsgi_application
from django.db.models import Q
# Environment can use the models as if inside the Django app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

from beta_invite.util import email_sender
from dashboard.models import Candidate


def send_candidates_emails():

    candidates = Candidate.objects.filter(~Q(user=None), user__gender_id=None).order_by('-user_id')  # [:100]

    candidates = [c for c in candidates]

    print([c.user_id for c in candidates])
    email_sender.send(objects=candidates,
                      language_code='es',
                      body_input='candidates_form_reminder_email_body',
                      subject='Información adicional')


# Precaution: If script imported for another module, this lines avoid the execution of this entire file
if __name__ == '__main__':
    send_candidates_emails()
