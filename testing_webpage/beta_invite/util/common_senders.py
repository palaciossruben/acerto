"""Has common functions of the senders"""
import os
from django.conf import settings
from decouple import config

import common
from beta_invite.models import WorkAreaSegment

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


def get_jobs_segment_url(segment_id):

    work_area_segment = WorkAreaSegment.objects.get(pk=segment_id)

    if work_area_segment:
        return HOST + '/trabajos?segment_code={segment_code}'.format(segment_code=work_area_segment.code)
    else:
        return ''


def get_campaign_url(candidate):

    if hasattr(candidate, 'campaign_id') and candidate.campaign_id:
        return candidate.campaign.get_url_for_candidates()
    else:
        return ''


def get_campaign_salary_range(candidate):
    if candidate and candidate.campaign_id:
        return candidate.campaign.get_campaign_salary_range()
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


def get_campaign_city_name(candidate):
    return candidate.campaign.get_campaign_city_name() if candidate and candidate.campaign else ''


def get_campaign_description(candidate, language_code):
    """
    For a object that has no associated campaign it will not return the title
    Args:
        candidate: User or Contact object.
    Returns: string with title
    """
    return candidate.campaign.get_description(language_code) if candidate and candidate.campaign else ''


def get_cv_url(user):
    return HOST + '/servicio_de_empleo/add_cv?user_id={user_id}'.format(user_id=user.id)


def get_file_path():
    return os.path.dirname(os.path.abspath(__file__))


def get_email_path():
    return os.path.join(get_file_path(), 'emails')


def get_message_path():
    return os.path.join(get_file_path(), 'messages')


def get_public_post_path():
    return os.path.join(get_file_path(), 'public_posts')


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
              }

    params.update(get_basic_params(override_dict))
    return params


def get_params_with_candidate(candidate, language_code='es', override_dict={}):
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
              'campaign': get_campaign_name(candidate, language_code),
              'campaign_url': get_campaign_url(candidate),
              'campaign_salary_range': get_campaign_salary_range(candidate),
              'campaign_city': get_campaign_city_name(candidate),
              'campaign_description': get_campaign_description(candidate, language_code)
              }

    if hasattr(candidate.user.work_area, 'segment_id'):
        params['jobs_url_by_workarea'] = get_jobs_segment_url(candidate.user.work_area.segment_id)

    if hasattr(candidate, 'campaign_id'):
        params['test_url'] = get_test_url(candidate.user, candidate.campaign)
        params['video_url'] = get_video_url(candidate.user, candidate.campaign)
        params['additional_info_url'] = get_additional_info_url(candidate)

    params.update(get_basic_params(override_dict))
    return params


def get_params_with_campaign(campaign, language_code='es', override_dict={}):
    """
    Args:
        campaign: Object.
        language_code: just that.
        override_dict: Dictionary that changes the default values.
    Returns:
    """
    params = {'campaign_name': campaign.title_es if language_code == 'es' else campaign.title,
              'campaign_url': campaign.get_url_for_candidates(),
              'campaign_salary_range': campaign.get_campaign_salary_range(),
              'campaign_city': campaign.get_campaign_city_name(),
              'campaign_description': campaign.get_description(language_code),
              'total_applicant_candidates': common.get_application_candidates_count(campaign),
              'total_relevant_candidates': common.get_relevant_candidates_count(campaign),
              'total_recommended_candidates': common.get_recommended_candidates_count(campaign),
              'campaign_summary_url': campaign.get_url_for_company(),
              'business_campaign_url': campaign.get_url_for_company(),
              }

    business_user = common.get_business_user_with_campaign(campaign)
    if business_user:
        params['name'] = get_first_name(business_user.name)
        params['complete_name'] = business_user.name.title()

    params.update(get_basic_params(override_dict))
    return params


def get_params_with_business_user(business_user, language_code='es', override_dict={}):
    """
        Args:
            business_user: Object.
            language_code: just that.
            override_dict: Dictionary that changes the default values.
        Returns:
        """
    params = {'name': get_first_name(business_user.name),
              'complete_name': business_user.name.title(),
             }

    params.update(get_basic_params(override_dict))
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
        try:
            with open(os.path.join(path, body_input), encoding='utf-8') as fp:
                return fp.read()
        except FileNotFoundError:  # tries on both folders, emails and messages
            with open(os.path.join(get_message_path(), body_input), encoding='utf-8') as fp:
                return fp.read()
    else:
        return body_input


def process_inputs(with_localization, language_code, body_input, objects):
    if with_localization and language_code != 'en':
        body_input += '_{}'.format(language_code)

    if type(objects) != list:
        objects = [objects]

    return body_input, objects
