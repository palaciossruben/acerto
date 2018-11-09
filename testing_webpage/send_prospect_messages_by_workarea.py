import os
from django.core.wsgi import get_wsgi_application
from django.db.models import Q

# Environment can use the models as if inside the Django app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()
from beta_invite.util import messenger_sender
from beta_invite.models import WorkAreaSegment
from dashboard.models import Candidate, State, Campaign


def candidates_filter(candidates):

    user_ids = set()
    filtered_candidates = list()

    for c in candidates:
        if c.user_id not in user_ids:
            user_ids.add(c.user_id)
            filtered_candidates.append(c)
    return filtered_candidates


def work_area_with_campaigns_filter(candidates):

    final_candidates = list()

    for c in candidates:

        segment = WorkAreaSegment.objects.get(pk=c.user.work_area.segment_id)

        campaigns = Campaign.objects.filter(~Q(title_es=None),
                                            state__code__in=['I', 'A'],
                                            removed=False,
                                            work_area__segment__code=segment.code)
        if len(campaigns) > 0:
            final_candidates.append(c)

    return final_candidates


def send_prospect_messages(segment_code):

    candidates = Candidate.objects.filter(~Q(user=None),
                                          ~Q(user__phone=None),
                                          ~Q(state__in=State.objects.filter(code__in=['STC', 'GTJ']).all()),
                                          ~Q(user__work_area__segment=None),
                                          removed=False)

    candidates = [c for c in candidates]

    new_candidates = candidates_filter(candidates)

    final_candidates = work_area_with_campaigns_filter(new_candidates)

    print(len(candidates))
    print(len(new_candidates))
    print(len(final_candidates))

    messenger_sender.send(candidates=final_candidates,
                          language_code='es',
                          body_input='prospects_invitation_message_body')


# Precaution: If script imported for another module, this lines avoid the execution of this entire file
if __name__ == '__main__':
    send_prospect_messages('II')
