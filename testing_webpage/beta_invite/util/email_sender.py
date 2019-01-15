import requests
import unicodedata
from decouple import config
from django.conf import settings

import common
from dashboard.models import Candidate, User, Campaign
from beta_invite.util import common_senders
from business.models import BusinessUser

INTERNAL_TEAM = ['santiago@peaku.co', 'juan@peaku.co', 'juan.rendon@peaku.co']
TESTING_TEAM = ['juan@peaku.co', 'juan.rendon@peaku.co', 'ing.pendiente@gmail.com']


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


def mail_gun_post(recipients, subject, body, html, attachment):
    try:

        requests.post(config('mailgun_url'),
                      auth=("api", config('mailgun_api_key')),
                      data={"from": config('email'),
                            "to": recipients,
                            "subject": subject,
                            "text": body,
                            "html": html},
                      files=get_files(attachment), )
    except ConnectionError:
        pass


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

    html = body.replace('\n', '<br>') + '<br><a href=%unsubscribe_url%>Desuscribir</a>'

    if settings.DEBUG:
        recipients = validate_emails(TESTING_TEAM)
    else:
        recipients = validate_emails(recipients)

    if len(recipients) > 0:
        mail_gun_post(recipients, subject, body, html, attachment)


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

    for an_object in objects:

        if isinstance(an_object, Candidate):
            params = common_senders.get_params_with_candidate(an_object, language_code, override_dict)
            recipients = an_object.user.email
        elif isinstance(an_object, User):
            params = common_senders.get_params_with_user(an_object, override_dict)
            recipients = an_object.email
        elif isinstance(an_object, BusinessUser):
            params = common_senders.get_params_with_business_user(an_object, override_dict)
            recipients = an_object.email
        elif isinstance(an_object, Campaign):
            params = common_senders.get_params_with_campaign(an_object)
            business_user = common.get_business_user_with_campaign(an_object)
            recipients = business_user.email
        else:
            raise NotImplementedError('Unimplemented email params for class: {}'.format(type(an_object)))

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
        if c.user.get_curriculum_url() != '#':
            cv_url = c.user.get_curriculum_url()
        else:
            cv_url = 'Hoja de vida no disponible'

        if c.campaign is not None:
            campaign_name = c.campaign.name
        else:
            campaign_name = None

        resume_summaries.append('Campaña: {campaign}\n'
                                'Nombre: {name}\n'
                                'Email: {email}\n'
                                'Hoja de vida: \n{cv_url}'.format(campaign=campaign_name,
                                                                  name=remove_accents(c.user.name),
                                                                  email=c.user.email,
                                                                  country=c.get_country_name(),
                                                                  profession=c.get_profession_name(),
                                                                  education=c.get_education_name(),
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

    send_with_mailgun(recipients=INTERNAL_TEAM,
                      subject=subject,
                      body=body)
