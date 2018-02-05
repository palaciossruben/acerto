import os
from datetime import datetime, timedelta
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
    if len(candidates) > 0:
        email_sender.send_report(language_code='es',
                                 body_filename='daily_report_email_body',
                                 subject='Daily report',
                                 recipients=['juan@peaku.co', 'santiago@peaku.co'],
                                 candidates=candidates)


def send_campaign_report(recipients, campaign_id):

    campaign = Campaign.objects.get(pk=campaign_id)
    candidates = Candidate.objects.filter(created_at__range=[str(timezone.now() - timedelta(days=1)), str(timezone.now())],
                                          campaign=campaign)

    # Only send if there is something.
    if len(candidates) > 0:
        email_sender.send_report(language_code='es',
                                 body_filename='daily_report_email_body',
                                 subject='Reporte diario para {campaign_name}'.format(campaign_name=campaign.title_es),
                                 recipients=recipients,
                                 candidates=candidates)
# b_user = BusinessUser.objects.get(pk=42)
# campaign = Campaign.objects.get(pk=42)


def business_daily_report():
    business_users = BusinessUser.objects.all()
    for business_user in business_users:
        for campaign in business_user.campaigns.filter(active=True):

            candidates = Candidate.objects.filter(
                created_at__range=[str(timezone.now() - timedelta(days=1)), str(timezone.now())],
                campaign=campaign,
                removed=False)

            # Only send if there is something.
            if len(candidates) > 0:
                email_sender.send_report(language_code='es',
                                         body_filename='business_daily_report_email_body',
                                         subject='Reporte diario de nuevos candidatos',
                                         recipients=[business_user.email, 'juan.rendon@peaku.co'],
                                         candidates=candidates)


# sends iOS candidates
# TODO: add pablo? 'mmedina@tappsi.co'
send_campaign_report(['juan@peaku.co', 'santiago@peaku.co'], campaign_id=10)
business_daily_report()
# send_general_report()
