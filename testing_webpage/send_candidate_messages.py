import os
from django.core.wsgi import get_wsgi_application
from django.db.models import Q

# Environment can use the models as if inside the Django app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()
from beta_invite.util import messenger_sender
from dashboard.models import Candidate
from beta_invite.models import User


def candidates_filter(candidates):

    user_ids = set()
    filtered_candidates = list()

    for c in candidates:
        if c.user_id not in user_ids:
            user_ids.add(c.user_id)
            filtered_candidates.append(c)
    return filtered_candidates


def send_candidates_messages():

    candidates = Candidate.objects.filter(~Q(user=None),
                                          ~Q(user__phone=None),
                                          user__gender_id=None).order_by('-user_id')  # [:100]

    candidates = [c for c in candidates]

    new_candidates = candidates_filter(candidates)

    print(len(candidates))
    print(len(new_candidates))

    # print([c.user_id for c in candidates])
    messenger_sender.send(candidates=new_candidates,
                          language_code='es',
                          body_input='candidates_form_reminder_message_body')


# Precaution: If script imported for another module, this lines avoid the execution of this entire file
if __name__ == '__main__':
    send_candidates_messages()
