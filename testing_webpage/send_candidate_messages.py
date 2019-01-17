import os
from django.core.wsgi import get_wsgi_application
from django.db.models import Q

# Environment can use the models as if inside the Django app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()
from beta_invite.util import messenger
from dashboard.models import Candidate


def candidates_filter(candidates):

    user_ids = set()
    filtered_candidates = list()

    for c in candidates:
        if c.user_id not in user_ids:
            user_ids.add(c.user_id)
            filtered_candidates.append(c)
    return filtered_candidates


def send_candidates_messages():

    candidates = Candidate.objects.filter(user__work_area__code__in=['IT', 'I', 'IC'],
                                          user__salary__gte=2000000,
                                          user__salary__lte=10000000,
                                          user__city__id=2).order_by('-id')[1:20]  # City=Bogotá

    #candidates = list(Candidate.objects.filter(user__pk=1929))

    candidates = candidates_filter(candidates)

    messenger.send(objects=candidates,
                   language_code='en',
                   body_input='comodin')

    print(len(candidates))


if __name__ == '__main__':
    send_candidates_messages()
