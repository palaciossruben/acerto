"""
Sends messages.
"""
import common
from beta_invite.util import common_senders
from dashboard.models import Message, Candidate
from beta_invite.models import CampaignMessage, Campaign


def save_candidate_messages(candidates, body_input, body_is_filename, language_code, override_dict, original_body_input):
    # More obscurity for very needed speed... sorry
    messages = Message.objects.bulk_create([
        Message(candidate=c,
                text=common_senders.get_body(body_input,
                                             body_is_filename=body_is_filename)
                .format(**common_senders.get_params_with_candidate(c,
                                                                   language_code,
                                                                   override_dict)),
                filename=original_body_input if body_is_filename else None)
        for c in candidates])

    common.bulk_save(messages)


def save_campaign_messages(campaigns, body_input, body_is_filename, language_code, override_dict):
    # More obscurity for very needed speed... sorry
    messages = CampaignMessage.objects.bulk_create([
        CampaignMessage(campaign=c,
                        text=common_senders.get_body(body_input,
                                                     body_is_filename=body_is_filename)
                        .format(**common_senders.get_params_with_campaign(c,
                                                                          language_code,
                                                                          override_dict))
                        )
        for c in campaigns])

    common.bulk_save(messages)


def send(objects, language_code, body_input, with_localization=True, body_is_filename=True,
         override_dict={}):
    """
    Sends a message
    Args:
        objects: a Candidate object or a list of Candidates or Business Users. has fields 'name', 'email' and campaign
        language_code: eg: 'es' or 'en'
        body_input: the filename of the body content or the body itself
        with_localization: Boolean indicating whether emails are translated according to browser configuration.
        body_is_filename: Boolean indicating whether the body_input is a filename or a string with content.
        override_dict: Dictionary where keys are fields and values to override the keyword behavior.
    Returns: Sends message to queue
    """

    original_body_input = body_input

    body_input, objects = common_senders.process_inputs(with_localization=with_localization,
                                                        language_code=language_code,
                                                        body_input=body_input,
                                                        objects=objects)

    # validates, it is not empty
    if len(objects) == 0:
        return

    # TODO: implement for new BusinessUser
    if type(objects[0]) is Candidate:
        save_candidate_messages(objects, body_input, body_is_filename, language_code, override_dict, original_body_input)
    elif type(objects[0]) is Campaign:
        save_campaign_messages(objects, body_input, body_is_filename, language_code, override_dict)
    else:
        raise NotImplementedError('object: {} cannot be processed by send method in our API'.format(objects[0]))
