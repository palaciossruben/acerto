"""Has common functions of the senders"""
import os
from django.conf import settings
from decouple import config
import common


if settings.DEBUG:
    HOST = '//127.0.0.1:8000'
else:
    HOST = 'https://peaku.co'


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


def get_test_url(user, campaign):

    if user and campaign:
        return HOST + '/servicio_de_empleo/pruebas?campaign_id={campaign_id}&user_id={user_id}'.format(user_id=user.id,
                                                                                                       campaign_id=campaign.id)
    else:
        return ''


def get_additional_info_url(candidate):

    if candidate:
        return HOST + '/servicio_de_empleo/additional_info?candidate_id={candidate_id}'.format(candidate_id=candidate.pk)
    else:
        return ''


def get_video_url(user, campaign):
    if user and campaign:
        return HOST + '/servicio_de_empleo/interview/1?campaign_id={campaign_id}&user_id={user_id}'.format(user_id=user.id,
                                                                                                           campaign_id=campaign.id)
    else:
        return ''


def get_business_campaign_url(campaign):
    if campaign:
        return HOST + '/servicio_de_empleo?campaign_id={campaign_id}'.format(campaign_id=campaign.id)
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
    return HOST + '/servicio_de_empleo/add_cv?user_id={user_id}'.format(user_id=user.id)


def get_file_path():
    return os.path.dirname(os.path.abspath(__file__))


def get_email_path():
    return os.path.join(get_file_path(), 'emails')


def get_message_path():
    return os.path.join(get_file_path(), 'messages')


def get_basic_params(override_dict={}):
    """
    Limited version of the get_params_with_candidate(). For specific cases.
    Args:
        override_dict: Dictionary that changes the default values.
    Returns:
    """
    params = {'sender_name': config('sender_name'),
              'sender_position': config('sender_position'),
              'peaku_address': config('peaku_address'),
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

    params = {'name': get_first_name(user.name),
              'complete_name': user.name.title(),
              'cv_url': get_cv_url(user),
              'sender_name': config('sender_name'),
              'sender_position': config('sender_position'),
              'peaku_address': config('peaku_address'),
              }

    for k, v in override_dict.items():
        params[k] = v

    return params


def get_params_with_candidate(candidate, language_code, override_dict={}):
    """
    Args:
        candidate: Object.
        language_code: just that.
        override_dict: Dictionary that changes the default values.
    Returns:
    """

    params = {'name': get_first_name(candidate.user.name),
              'complete_name': candidate.user.name.title(),
              'cv_url': get_cv_url(candidate.user),
              'sender_name': config('sender_name'),
              'sender_position': config('sender_position'),
              'peaku_address': config('peaku_address'),
              'campaign': get_campaign_name(candidate, language_code),
              'campaign_url': get_campaign_url(candidate)}

    if hasattr(candidate, 'campaign_id'):
        params['test_url'] = get_test_url(candidate.user, candidate.campaign)
        params['video_url'] = get_video_url(candidate.user, candidate.campaign)
        params['additional_info_url'] = get_additional_info_url(candidate)
    for k, v in override_dict.items():
        params[k] = v

    return params


def get_body(body_input, body_is_filename=True, path=get_email_path()):
    """
    Args:
        body_is_filename: Boolean
        body_input: filename or text body.
        path: either to message or email
    Returns:
    """
    if body_is_filename:
        with open(os.path.join(path, body_input), encoding='utf-8') as fp:
            return fp.read()
    else:
        return body_input


def process_inputs(with_localization, language_code, body_input, candidates):
    if with_localization and language_code != 'en':
        body_input += '_{}'.format(language_code)

    if type(candidates) != list:
        candidates = [candidates]

    return body_input, candidates
