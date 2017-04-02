import os
import smtplib

from email.mime.text import MIMEText


def get_current_path():
    return os.path.dirname(os.path.abspath(__file__))


def get_first_name(complete_name):
    """
    First trims, then takes the first name.
    :param complete_name: string with whatever the user name is.
    :return: first name
    """
    return complete_name.strip().split()[0]


def send(user):

    # Open a plain text file for reading.  For this example, assume that
    # the text file contains only ASCII characters.
    with open(get_current_path() + '/email_body') as fp:
        msg = MIMEText(fp.read().format(name=get_first_name(user.name)))

    msg['Subject'] = 'Welcome to PeakU'
    msg['From'] = 'biosolardecolombia@gmail.com'
    msg['To'] = user.email

    # Send the message via our own SMTP server.
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("biosolardecolombia", "Aa112358")

    server.send_message(msg)
    server.quit()
