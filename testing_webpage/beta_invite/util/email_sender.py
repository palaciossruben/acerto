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


def send_email(user, password, recipient, subject, body):

    gmail_user = user
    gmail_pwd = password
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(gmail_user, gmail_pwd)
    server.sendmail(FROM, TO, message)
    server.close()


def send(user, language_code, body_filename, subject):
    """
    Sends an email
    Args:
        user: Any object that has fields 'name' and 'email'
        language_code: eg: 'es' or 'en'
        body_filename: the filename of the body content
        subject: string with the email subject
    Returns: Sends email
    """

    if language_code != 'en':
        body_filename += '_{}'.format(language_code)

    with open(os.path.join(get_current_path(), body_filename)) as fp:
        body = fp.read().format(name=get_first_name(user.name))

    sender_data = read_email_credentials()

    send_email(user=sender_data['email'],
               password=sender_data['password'],
               recipient=user.email,
               subject=subject,
               body=body)


def send_internal(contact, language_code, body_filename, subject):
    """
    Sends an email to the internal team.
    Args:
        contact: Any object that has fields 'name' and 'email'
        language_code: eg: 'es' or 'en'
        body_filename: the filename of the body content
        subject: string with the email subject
    Returns: Sends email
    """

    internal_team = ['santiago@peaku.co', 'juan@peaku.co', 'santiagopsa@gmail.com']

    if language_code != 'en':
        body_filename += '_{}'.format(language_code)

    with open(os.path.join(get_current_path(), body_filename)) as fp:
        body = fp.read().format(name=contact.name,
                                email=contact.email,
                                phone=contact.phone,
                                message=contact.message)

    sender_data = read_email_credentials()

    send_email(user=sender_data['email'],
               password=sender_data['password'],
               recipient=internal_team,
               subject=subject,
               body=body)
