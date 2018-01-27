import os
from datetime import datetime, timedelta
from django.core.wsgi import get_wsgi_application

# Environment can use the models as if inside the Django app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

from beta_invite.models import Campaign
from beta_invite.util import email_sender
from dashboard.models import Candidate


def send_general_report():
    candidates = Candidate.objects.filter(created_at__range=[str(datetime.now() - timedelta(days=1)), str(datetime.now())])

    # Only send if there is something.
    if len(candidates) > 0:
        email_sender.send_report(language_code='es',
                                 body_filename='daily_report_email_body',
                                 subject='Daily report',
                                 recipients=['juan@peaku.co', 'santiago@peaku.co'],
                                 candidates=candidates)


def send_campaign_report(recipients, campaign_id):

    campaign = Campaign.objects.get(pk=campaign_id)
    candidates = Candidate.objects.filter(created_at__range=[str(datetime.now() - timedelta(days=1)), str(datetime.now())],
                                          campaign=campaign)

    # Only send if there is something.
    if len(candidates) > 0:
        email_sender.send_report(language_code='es',
                                 body_filename='daily_report_email_body',
                                 subject='Reporte diario para {campaign_name}'.format(campaign_name=campaign.title_es),
                                 recipients=recipients,
                                 candidates=candidates)


send_general_report()

# sends iOS candidates
# TODO: add pablo? 'mmedina@tappsi.co'
send_campaign_report(['juan@peaku.co', 'santiago@peaku.co'], campaign_id=10)
