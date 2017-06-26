import os
import json
import smtplib

from email.mime.text import MIMEText
from django.utils.translation import ugettext as _


def get_current_path():
    return os.path.dirname(os.path.abspath(__file__))


def get_first_name(complete_name):
    """
    First trims, then takes the first name.
    :param complete_name: string with whatever the user name is.
    :return: first name
    """
    return complete_name.strip().split()[0]


def read_email_credentials():
    """Returns a json with the credentials"""
    json_data = open(os.path.join(get_current_path(), "email_credentials.json")).read()
    return json.loads(json_data)


def send(user, language_code):

    # Open a plain text file for reading.  For this example, assume that
    # the text file contains only ASCII characters.

    body_filename = 'email_body'
    if language_code != 'en':
        body_filename += '_{}'.format(language_code)

    with open(os.path.join(get_current_path(), body_filename)) as fp:
        msg = MIMEText(fp.read().format(name=get_first_name(user.name)))

    email_data = read_email_credentials()

    msg['Subject'] = _('Welcome to PeakU')
    msg['From'] = email_data['email']
    msg['To'] = user.email

    # Send the message via our own SMTP server.
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_data['email'], email_data['password'])

    server.send_message(msg)
    server.quit()
