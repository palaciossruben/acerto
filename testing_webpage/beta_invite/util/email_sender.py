import os
import json
import smtplib
import requests
import unicodedata


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
    json_data = open(os.path.join(get_current_path(), "email_credentials.json"), encoding='utf-8').read()
    return json.loads(json_data)


def send_email_through_smtp(user, password, recipient, subject, body):

    # TODO: deactivates mail temporarily
    return

    gmail_user = user
    gmail_pwd = password
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = remove_accents(str(subject))
    TEXT = remove_accents(str(body))

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(gmail_user, gmail_pwd)
    server.sendmail(FROM, TO, message)
    server.close()


def send_email_with_mailgun(sender, recipients, subject, body, mail_gun_url, mailgun_api_key):
    """
    Sends emails over mailgun service
    Args:
        sender: an email.
        recipients: email or lists of emails.
        subject: email subject, string
        body: email body, string
        mail_gun_url: string
        mailgun_api_key: string
    Returns: sends emails.
    """
    recipients = recipients if type(recipients) is list else [recipients]

    # TODO: can this be removed. Can mailgun manage unicode?

    return requests.post(
        mail_gun_url,
        auth=("api", mailgun_api_key),
        data={"from": sender,
              "to": recipients,
              "subject": subject,
              "text": body})


def get_test_url(user):

    if hasattr(user, 'campaign_id'):
        return 'http://peaku.co/beta_invite/long_form/post?campaign_id={campaign_id}&user_id={user_id}'.format(user_id=user.id,
                                                                                                               campaign_id=user.campaign_id)
    else:
        return ''


def get_campaign_name(user, language_code):
    """
    For a object that has no associeted campaign it will not return the title
    Args:
        user: User or Contact object.
    Returns: string with title
    """
    if user and hasattr(user, 'campaign') and user.campaign:
        if language_code == 'es':
            return user.campaign.title_es
        else:
            return user.campaign.title

    return ''


def get_cv_url(user):
    return 'http://peaku.co/beta_invite/long_form/add_cv?user_id={user_id}'.format(user_id=user.id)


def send(users, language_code, body_input, subject, with_localization=True, body_is_filename=True):
    """
    Sends an email
    Args:
        users: Any object that has fields 'name' and 'email' or a list of users.
        language_code: eg: 'es' or 'en'
        body_input: the filename of the body content or the body itself
        subject: string with the email subject
        with_localization: Boolean indicating whether emails are translated according to browser configuration.
        body_is_filename: Boolean indicating whether the body_input is a filename or a string with content.
    Returns: Sends email
    """

    if with_localization and language_code != 'en':
        body_input += '_{}'.format(language_code)

    if type(users) != list:
        users = [users]

    sender_data = read_email_credentials()

    for user in users:

        if body_is_filename:
            with open(os.path.join(get_current_path(), body_input), encoding='utf-8') as fp:
                body = fp.read().format(name=get_first_name(user.name),
                                        test_url=get_test_url(user),
                                        cv_url=get_cv_url(user),
                                        sender_name=sender_data['sender_name'],
                                        sender_position=sender_data['sender_position'],
                                        peaku_address=sender_data['peaku_address'],
                                        campaign=get_campaign_name(user, language_code),)
        else:
            body = body_input.format(name=get_first_name(user.name),
                                     test_url=get_test_url(user),
                                     cv_url=get_cv_url(user),
                                     sender_name=sender_data['sender_name'],
                                     sender_position=sender_data['sender_position'],
                                     peaku_address=sender_data['peaku_address'],
                                     campaign=get_campaign_name(user, language_code),)

        send_email_with_mailgun(sender=sender_data['email'],
                                recipients=user.email,
                                subject=subject.format(name=get_first_name(user.name)),
                                body=body,
                                mail_gun_url=sender_data['mailgun_url'],
                                mailgun_api_key=sender_data['mailgun_api_key'])


def remove_accents_in_string(element):
    """
    Args:
        element: anything.
    Returns: Cleans accents only for strings.
    """
    if isinstance(element, str):
        return ''.join(c for c in unicodedata.normalize('NFD', element) if unicodedata.category(c) != 'Mn')
    else:
        return element


def remove_accents(an_object):
    """
    Several different objects can be cleaned.
    Args:
        an_object: can be list, string, tuple or dict
    Returns: the cleaned obj, or a exception if not implemented.
    """
    if isinstance(an_object, str):
        return remove_accents_in_string(an_object)
    elif isinstance(an_object, list):
        return [remove_accents_in_string(e) for e in an_object]
    elif isinstance(an_object, tuple):
        return tuple([remove_accents_in_string(e) for e in an_object])
    elif isinstance(an_object, dict):
        return {remove_accents_in_string(k): remove_accents_in_string(v) for k, v in an_object.items()}
    else:
        raise NotImplementedError


def create_nice_resumes_message(users):

    resume_summaries = []
    for u in users:
        if u.curriculum_url != '#':
            cv_url = 'http://peaku.co/static/{url}'.format(url=u.curriculum_url)
        else:
            cv_url = 'no cv available'

        if u.campaign is not None:
            campaign_name = u.campaign.name
        else:
            campaign_name = 'unknown'

        resume_summaries.append('campaign: {campaign_name}\n'
                                'name: {name}\n'
                                'email: {email}\n'
                                'country: {country}\n'
                                'profession: {profession}\n'
                                'education: {education}\n'
                                'cv: \n{cv_url}'.format(campaign_name=campaign_name,
                                                        name=remove_accents(u.name),
                                                        email=u.email,
                                                        country=u.country.name,
                                                        profession=u.profession.name,
                                                        education=u.education.name,
                                                        cv_url=cv_url))
    return '\n\n'.join(resume_summaries)


def send_report(language_code, body_filename, subject, recipients, users):
    """
    Sends an email
    Args:
        language_code: eg: 'es' or 'en'
        body_filename: the filename of the body content
        subject: string with the email subject
        recipients: email send to.
    Returns: Sends email
    """

    if language_code != 'en':
        body_filename += '_{}'.format(language_code)

    resumes = create_nice_resumes_message(users)
    sender_data = read_email_credentials()

    with open(os.path.join(get_current_path(), body_filename)) as fp:
        body = fp.read().format(new_resumes=resumes,
                                sender_name=sender_data['sender_name'],
                                sender_position=sender_data['sender_position'],
                                peaku_address=sender_data['peaku_address'],)

    send_email_with_mailgun(sender=sender_data['email'],
                            recipients=recipients,
                            subject=subject,
                            body=body,
                            mail_gun_url=sender_data['mailgun_url'],
                            mailgun_api_key=sender_data['mailgun_api_key'])


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

    internal_team = ['santiago@peaku.co', 'juan@peaku.co']

    if language_code != 'en':
        body_filename += '_{}'.format(language_code)

    with open(os.path.join(get_current_path(), body_filename)) as fp:

        try:
            message = contact.message
        except AttributeError:  # missing field
            message = ''

        body = fp.read().format(name=contact.name,
                                email=contact.email,
                                phone=contact.phone,
                                message=message)

    sender_data = read_email_credentials()

    send_email_with_mailgun(sender=sender_data['email'],
                            recipients=internal_team,
                            subject=subject,
                            body=body,
                            mail_gun_url=sender_data['mailgun_url'],
                            mailgun_api_key=sender_data['mailgun_api_key'])
