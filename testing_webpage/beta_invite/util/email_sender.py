import os
import json
import smtplib
import requests
import unicodedata
from django.conf import settings

if settings.DEBUG:
    host = '//127.0.0.1:8000'
else:
    host = 'https://peaku.co'


def get_email_path():
    return os.path.dirname(os.path.abspath(__file__)) + '/emails'


def get_first_name(complete_name):
    """
    First trims, then takes the first name. It ensures a title format (First letter of each word is capital)
    :param complete_name: string with whatever the user name is.
    :return: first name
    """
    if len(complete_name) > 0:
        return complete_name.strip().split()[0].title()
    else:
        return ''


def read_email_credentials():
    """Returns a json with the credentials"""
    json_data = open(os.path.join(get_email_path(), "email_credentials.json"), encoding='utf-8').read()
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


def get_files(attachment):
    if attachment:
        return [("attachment", (attachment, open(attachment, "rb").read()))]
    else:
        return []


def validate_emails(emails):
    """
    Puts everything as list
    Filters for different from None
    :param emails: list of emails, or a single email.
    :return:
    """
    emails = emails if type(emails) is list else [emails]
    return [e for e in emails if e is not None]


def send_with_mailgun(sender_data, recipients, subject, body, attachment=None):
    """
    Sends emails over mailgun service
    Args:
        sender_data: an email.
        recipients: email or lists of emails.
        subject: email subject, string
        body: email body, string
        attachment: optional param for attaching content to email
    Returns: sends emails.
    """

    recipients = validate_emails(recipients)

    if len(recipients) > 0:
        return requests.post(
             sender_data['mailgun_url'],
             auth=("api", sender_data['mailgun_api_key']),
             data={"from": sender_data['email'],
                   "to": recipients,
                   "subject": subject,
                   "text": body},
             files=get_files(attachment),)


def get_test_url(user, campaign):

    if user and campaign:
        return host + '/servicio_de_empleo/pruebas?campaign_id={campaign_id}&user_id={user_id}'.format(user_id=user.id,
                                                                                                       campaign_id=campaign.id)
    else:
        return ''


def get_video_url(user, campaign):
    if user and campaign:
        return host+'/servicio_de_empleo/interview/1?campaign_id={campaign_id}&user_id={user_id}'.format(user_id=user.id,
                                                                                                         campaign_id=campaign.id)
    else:
        return ''


def get_business_campaign_url(campaign):
    if campaign:
        return host+'/servicio_de_empleo?campaign_id={campaign_id}'.format(campaign_id=campaign.id)
    else:
        return ''


def get_campaign_url(candidate):

    if hasattr(candidate, 'campaign_id') and candidate.campaign_id:
        return candidate.campaign.get_url()
    else:
        return ''


def get_campaign_name(candidate, language_code):
    """
    For a object that has no associated campaign it will not return the title
    Args:
        candidate: User or Contact object.
    Returns: string with title
    """
    if candidate and hasattr(candidate, 'campaign') and candidate.campaign:
        if language_code == 'es':
            return candidate.campaign.title_es
        else:
            return candidate.campaign.title

    return ''


def get_cv_url(user):
    return host+'/servicio_de_empleo/add_cv?user_id={user_id}'.format(user_id=user.id)


def get_basic_params(override_dict={}):
    """
    Limited version of the get_params_with_candidate(). For specific cases.
    Args:
        override_dict: Dictionary that changes the default values.
    Returns:
    """
    sender_data = read_email_credentials()
    params = {'sender_name': sender_data['sender_name'],
              'sender_position': sender_data['sender_position'],
              'peaku_address': sender_data['peaku_address'],
              }

    for k, v in override_dict.items():
        params[k] = v

    return params


def get_params_with_user(user, override_dict={}):
    """
    Limited version of the get_params_with_candidate(). For specific cases.
    Args:
        user: Object.
        override_dict: Dictionary that changes the default values.
    Returns:
    """

    sender_data = read_email_credentials()
    params = {'name': get_first_name(user.name),
              'complete_name': user.name.title(),
              'cv_url': get_cv_url(user),
              'sender_name': sender_data['sender_name'],
              'sender_position': sender_data['sender_position'],
              'peaku_address': sender_data['peaku_address'],
              }

    for k, v in override_dict.items():
        params[k] = v

    return params


# TODO: the code is duplicated
def get_params_for_candidate(candidate, language_code, override_dict={}):
    """
    Args:
        candidate: Object.
        language_code: just that.
        override_dict: Dictionary that changes the default values.
    Returns:
    """

    sender_data = read_email_credentials()
    params = {'name': get_first_name(candidate.user.name),
              'complete_name': candidate.user.name.title(),
              'cv_url': get_cv_url(candidate.user),
              'sender_name': sender_data['sender_name'],
              'sender_position': sender_data['sender_position'],
              'peaku_address': sender_data['peaku_address'],
              'campaign': get_campaign_name(candidate, language_code),
              'campaign_url': get_campaign_url(candidate)}

    if hasattr(candidate, 'campaign_id'):
        params['test_url'] = get_test_url(candidate.user, candidate.campaign)
        params['video_url'] = get_video_url(candidate.user, candidate.campaign)

    for k, v in override_dict.items():
        params[k] = v

    return params


def get_body(body_input, body_is_filename=True):
    """
    Args:
        body_is_filename: Boolean
        body_input: filename or text body.
    Returns:
    """
    if body_is_filename:
        with open(os.path.join(get_email_path(), body_input), encoding='utf-8') as fp:
            return fp.read()
    else:
        return body_input


# TODO: the code is duplicated
def send(users, language_code, body_input, subject, with_localization=True, body_is_filename=True, override_dict={},
         attachment=None):
    """
    Sends an email
    Args:
        users: Any object that has fields 'name' and 'email' or a list of users.
        language_code: eg: 'es' or 'en'
        body_input: the filename of the body content or the body itself
        subject: string with the email subject
        with_localization: Boolean indicating whether emails are translated according to browser configuration.
        body_is_filename: Boolean indicating whether the body_input is a filename or a string with content.
        override_dict: Dictionary where keys are fields and values to override the keyword behavior.
        attachment: optional param for adding attached file.
    Returns: Sends email
    """

    if with_localization and language_code != 'en':
        body_input += '_{}'.format(language_code)

    if type(users) != list:
        users = [users]

    sender_data = read_email_credentials()

    for user in users:

        params = get_params_with_user(user, override_dict)

        body = get_body(body_input, body_is_filename=body_is_filename)

        send_with_mailgun(sender_data=sender_data,
                          recipients=user.email,
                          subject=subject.format(**params),
                          body=body.format(**params),
                          attachment=attachment)


# TODO: the code is duplicated
def send_to_candidate(candidates, language_code, body_input, subject, with_localization=True, body_is_filename=True, override_dict={}):
    """
    Sends an email
    Args:
        candidates: a Candidate object or a list of Candidates. has fields 'name', 'email' and campaign
        language_code: eg: 'es' or 'en'
        body_input: the filename of the body content or the body itself
        subject: string with the email subject
        with_localization: Boolean indicating whether emails are translated according to browser configuration.
        body_is_filename: Boolean indicating whether the body_input is a filename or a string with content.
        override_dict: Dictionary where keys are fields and values to override the keyword behavior.
    Returns: Sends email
    """

    if with_localization and language_code != 'en':
        body_input += '_{}'.format(language_code)

    if type(candidates) != list:
        candidates = [candidates]

    sender_data = read_email_credentials()

    for candidate in candidates:

        params = get_params_for_candidate(candidate, language_code, override_dict)

        body = get_body(body_input, body_is_filename=body_is_filename)

        send_with_mailgun(sender_data=sender_data,
                          recipients=[candidate.user.email, 'juan.rendon@peaku.co'],
                          subject=subject.format(**params),
                          body=body.format(**params))


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


def create_nice_resumes_message(candidates):

    resume_summaries = []
    for c in candidates:
        if c.user.curriculum_url != '#':
            cv_url = 'https://peaku.co/static/{url}'.format(url=c.user.curriculum_url)
        else:
            cv_url = 'Hoja de vida no disponible'

        if c.campaign is not None:
            campaign_name = c.campaign.name
        else:
            campaign_name = None

        resume_summaries.append('Campaña: {campaign_name}\n'
                                'Nombre: {name}\n'
                                'Email: {email}\n'
                                'Hoja de vida: \n{cv_url}'.format(campaign_name=campaign_name,
                                                                  name=remove_accents(c.user.name),
                                                                  email=c.user.email,
                                                                  country=c.user.get_country_name(),
                                                                  profession=c.user.get_profession_name(),
                                                                  education=c.user.get_education_name(),
                                                                  cv_url=cv_url))

    return '\n\n'.join(resume_summaries)


def send_report(language_code, body_filename, subject, recipients, candidates):
    """
    Sends an email
    Args:
        language_code: eg: 'es' or 'en'
        body_filename: the filename of the body content
        subject: string with the email subject
        recipients: email send to.
        candidates: QuerySet of candidates
    Returns: Sends email
    """

    if language_code != 'en':
        body_filename += '_{}'.format(language_code)

    resumes = create_nice_resumes_message(candidates)
    sender_data = read_email_credentials()

    body = get_body(body_filename)
    d = get_basic_params()
    d['new_resumes'] = resumes
    body = body.format(**d)

    send_with_mailgun(sender_data=sender_data,
                      recipients=recipients,
                      subject=subject,
                      body=body)


def send_internal(contact, language_code, body_filename, subject, campaign=None):
    """
    Sends an email to the internal team.
    Args:
        contact: Any object that has fields 'name' and 'email'
        language_code: eg: 'es' or 'en'
        body_filename: the filename of the body content
        subject: string with the email subject
        campaign: campaign object for mail with campaign link

    Returns: Sends email
    """

    internal_team = ['juan@peaku.co', 'santiago@peaku.co', 'juan.rendon@peaku.co']

    if language_code != 'en':
        body_filename += '_{}'.format(language_code)

    try:
        message = contact.message
    except AttributeError:  # missing field
        message = ''

    body = get_body(body_filename)
    d = get_basic_params()
    d['message'] = message
    d['name'] = contact.name
    d['email'] = contact.email,
    d['phone'] = contact.phone,
    d['message'] = message,
    d['business_campaign_url'] = get_business_campaign_url(campaign)
    body = body.format(**d)

    sender_data = read_email_credentials()

    send_with_mailgun(sender_data=sender_data,
                      recipients=internal_team,
                      subject=subject,
                      body=body)
