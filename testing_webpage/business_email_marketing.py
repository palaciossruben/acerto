import os
from django.core.wsgi import get_wsgi_application

# Environment can use the models as if inside the Django app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

from beta_invite.util import email_sender
from business.models import User


# TODO: only works in Spanish
def send_email_marketing():

    with open('business_email_marketing.csv', encoding='UTF-8') as business_file:

        lines = business_file.read().split('\n')

        for line in lines:

            first_line = line.split(',')

            mail = first_line[1].strip()

            person_name = first_line[2].strip()

            user = User(name=person_name, email=mail)

            if person_name != '':
                subject = 'Correo para {complete_name}'
            else:
                subject = 'Correo para el gerente'

            email_sender.send(users=user,
                              language_code='es',
                              body_input='business_email_marketing_body',
                              subject=subject)


send_email_marketing()
