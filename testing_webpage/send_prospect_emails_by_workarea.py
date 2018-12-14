import os
from django.core.wsgi import get_wsgi_application
from django.db.models import Q
# Environment can use the models as if inside the Django app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

from beta_invite.util import email_sender
from dashboard.models import Candidate, State, Campaign
from beta_invite.models import User, WorkAreaSegment


def not_repeated_filter(candidates):

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


def work_area_with_campaigns_filter(candidates):

    final_candidates = list()

    for c in candidates:

        segment = WorkAreaSegment.objects.get(pk=c.user.work_area.segment_id)

        campaigns = Campaign.objects.filter(~Q(title_es=None),
                                            state__code__in=['A'],
                                            removed=False,
                                            work_area__segment__code=segment.code)
        if len(campaigns) > 0:
            final_candidates.append(c)

    return final_candidates


def send_prospect_emails():

    candidates = Candidate.objects.filter(~Q(user=None),
                                          ~Q(state__in=State.objects.filter(code__in=['STC', 'GTJ']).all()),
                                          ~Q(user__work_area__segment=None),
                                          removed=False)

    candidates = [c for c in candidates]

    new_candidates = not_repeated_filter(candidates)

    final_candidates = work_area_with_campaigns_filter(new_candidates)

    print(len(candidates))
    print(len(new_candidates))
    print(len(final_candidates))

    email_sender.send(objects=final_candidates,
                      language_code='es',
                      body_input='prospects_invitation_email_body',
                      subject='Ofertas')


# Precaution: If script imported for another module, this lines avoid the execution of this entire file
if __name__ == '__main__':
    send_prospect_emails()
