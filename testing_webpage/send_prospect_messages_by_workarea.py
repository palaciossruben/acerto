import os
from django.core.wsgi import get_wsgi_application
from django.db.models import Q

# Environment can use the models as if inside the Django app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()
from beta_invite.util import messenger_sender
from beta_invite.models import WorkAreaSegment
from dashboard.models import Candidate


def candidates_filter(candidates):

    users = set()
    new_candidates = list()

    for c in candidates:
        if c.user_id not in users:
            users.add(c.user_id)
            new_candidates.append(c.pk)
    return sorted(new_candidates)


def send_prospect_messages(segment_code):

    candidates = Candidate.objects.filter(~Q(user=None), ~Q(user__phone=None), ~Q(campaign__city=None),
                                          ~Q(state__in=[5, 7]), ~Q(removed=False),
                                          user__work_area__segment=WorkAreaSegment.objects.get(code=segment_code)).order_by('-user_id')#[:10]

    candidates = [c for c in candidates]

    print([c.user_id for c in candidates])

    new_candidates = candidates_filter(candidates)

    new_candidates = Candidate.objects.filter(pk__in=new_candidates).order_by('-user_id')

    print([c.user_id for c in new_candidates].__len__())

    messenger_sender.send(candidates=new_candidates,
                          language_code='es',
                          body_input='prospects_invitation_message_body')


# Precaution: If script imported for another module, this lines avoid the execution of this entire file
if __name__ == '__main__':
    send_prospect_messages('II')
