import os
from django.core.wsgi import get_wsgi_application
from django.db.models import Q
# Environment can use the models as if inside the Django app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

from beta_invite.util import email_sender
from dashboard.models import Candidate
from beta_invite.models import User


def candidates_filter(candidates):

    user_ids = set()
    filtered_candidates = list()

    users_emails = set()
    filtered_users = list()

    for c in candidates:
        users = User.objects.filter(pk=c.user_id)
        for u in users:
            if u.email not in users_emails:
                users_emails.add(u.email)
                filtered_users.append(u.pk)

    for c in candidates:
        if c.user_id not in user_ids and c.user_id in filtered_users:
            user_ids.add(c.user_id)
            filtered_candidates.append(c)

    return filtered_candidates


def send_users_additional_info_reminder():

    candidates = (Candidate.objects.filter(~Q(user=None), ~Q(user__email=None), user__gender_id=None).order_by('-user_id')
                  | Candidate.objects.filter(~Q(user=None), ~Q(user__email=None), user__experience=None).order_by('-user_id')
                  | Candidate.objects.filter(~Q(user=None), ~Q(user__email=None), user__city=None).order_by('-user_id')
                  | Candidate.objects.filter(~Q(user=None), ~Q(user__email=None), user__salary=None).order_by('-user_id')
                  | Candidate.objects.filter(~Q(user=None), ~Q(user__email=None), user__work_area=None).order_by('-user_id'))

    candidates = [c for c in candidates]

    new_candidates = candidates_filter(candidates)

    print(len(candidates))
    print(len(new_candidates))
    # test_candidates = new_candidates[:2]

    email_sender.send(objects=new_candidates,
                      language_code='es',
                      body_input='candidates_form_reminder_email_body',
                      subject='Información adicional')


# Precaution: If script imported for another module, this lines avoid the execution of this entire file
if __name__ == '__main__':
    send_users_additional_info_reminder()
