import os
import json
import requests
import unicodedata
from dashboard.models import Candidate
from beta_invite.util import common_senders


def read_email_credentials():
    """Returns a json with the credentials"""
    json_data = open(os.path.join(common_senders.get_email_path(), "email_credentials.json"), encoding='utf-8').read()
    return json.loads(json_data)


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


def send_with_mailgun(recipients, subject, body, attachment=None):
    """
    Sends emails over mailgun service
    Args:
        recipients: email or lists of emails.
        subject: email subject, string
        body: email body, string
        attachment: optional param for attaching content to email
    Returns: sends emails.
    """
    sender_data = read_email_credentials()
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


def send(objects, language_code, body_input, subject, with_localization=True, body_is_filename=True,
         override_dict={}, attachment=None):
    """
    Sends an email
    Args:
        objects: a Candidate object or a list of Candidates. has fields 'name', 'email' and campaign
        language_code: eg: 'es' or 'en'
        body_input: the filename of the body content or the body itself
        subject: string with the email subject
        with_localization: Boolean indicating whether emails are translated according to browser configuration.
        body_is_filename: Boolean indicating whether the body_input is a filename or a string with content.
        override_dict: Dictionary where keys are fields and values to override the keyword behavior.
        attachment: optional param for adding attached file.
    Returns: Sends email
    """

    body_input, objects = common_senders.process_inputs(with_localization, language_code, body_input, objects)

    for a_object in objects:

        if isinstance(a_object, Candidate):
            params = common_senders.get_params_with_candidate(a_object, language_code, override_dict)
            recipients = [a_object.user.email, 'juan.rendon@peaku.co']
        else:
            params = common_senders.get_params_with_user(a_object, override_dict)
            recipients = a_object.email

        body = common_senders.get_body(body_input, body_is_filename=body_is_filename)

        send_with_mailgun(recipients=recipients,
                          subject=subject.format(**params),
                          body=body.format(**params),
                          attachment=attachment)


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

    body = common_senders.get_body(body_filename)
    d = common_senders.get_basic_params()
    d['new_resumes'] = resumes
    body = body.format(**d)

    send_with_mailgun(recipients=recipients,
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

    body = common_senders.get_body(body_filename)
    d = common_senders.get_basic_params()
    d['message'] = message
    d['name'] = contact.name
    d['email'] = contact.email,
    d['phone'] = contact.phone,
    d['message'] = message,
    d['business_campaign_url'] = common_senders.get_business_campaign_url(campaign)
    body = body.format(**d)

    send_with_mailgun(recipients=internal_team,
                      subject=subject,
                      body=body)
