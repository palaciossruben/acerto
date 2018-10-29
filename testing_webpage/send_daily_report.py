import os
from datetime import timedelta
from django.core.wsgi import get_wsgi_application

# Environment can use the models as if inside the Django app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

from beta_invite.models import Campaign
from beta_invite.util import email_sender
from dashboard.models import Candidate
from business.models import BusinessUser
from django.utils import timezone


def send_general_report():
    candidates = Candidate.objects.filter(created_at__range=[str(timezone.now() - timedelta(days=1)), str(timezone.now())])

    # Only send if there is something.
    if True: #len(candidates) > 0:
        email_sender.send_report(language_code='es',
                                 body_filename='daily_report_email_body',
                                 subject='Daily report',
                                 recipients=['seleccion@peaku.co'],
                                 candidates=candidates)


def send_campaign_report(recipients, campaign_id):

    campaign = Campaign.objects.get(pk=campaign_id)
    candidates = Candidate.objects.filter(created_at__range=[str(timezone.now() - timedelta(days=1)), str(timezone.now())],
                                          campaign=campaign,
                                          state_id__in=[1, 8]
                                          )

    # Only send if there is something.
    if len(candidates) > 0:
        email_sender.send_report(language_code='es',
                                 body_filename='daily_report_email_body',
                                 subject='Reporte diario para {campaign_name}'.format(campaign_name=campaign.title_es),
                                 recipients=recipients,
                                 candidates=candidates)


def business_daily_report():
    business_users = BusinessUser.objects.all()
    for business_user in business_users:
        for campaign in business_user.campaigns.filter(state=2):

            candidates = Candidate.objects.filter(
                created_at__range=[str(timezone.now() - timedelta(days=1)), str(timezone.now())],
                campaign=campaign,
                removed=False,
                state_id__in=[5])

            # Only send if there is something.
            if len(candidates) > 0:
                email_sender.send_report(language_code='es',
                                         body_filename='business_daily_report_email_body',
                                         subject='Reporte de candidatos recomendados',
                                         recipients=[business_user.email, business_user.additional_email, 'seleccion@peaku.co'],
                                         candidates=candidates)


send_general_report()
business_daily_report()
