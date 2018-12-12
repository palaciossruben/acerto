"""
Sends messages.
"""
import common
from beta_invite.util import common_senders
from dashboard.models import Message


def send(candidates, language_code, body_input, with_localization=True, body_is_filename=True,
         override_dict={}):
    """
    Sends a message
    Args:
        candidates: a Candidate object or a list of Candidates. has fields 'name', 'email' and campaign
        language_code: eg: 'es' or 'en'
        body_input: the filename of the body content or the body itself
        with_localization: Boolean indicating whether emails are translated according to browser configuration.
        body_is_filename: Boolean indicating whether the body_input is a filename or a string with content.
        override_dict: Dictionary where keys are fields and values to override the keyword behavior.
    Returns: Sends message to queue
    """
    original_body_input = body_input

    body_input, candidates = common_senders.process_inputs(with_localization, language_code, body_input, candidates)

    # More obscurity for very needed speed... sorry
    messages = Message.objects.bulk_create([Message(candidate=c,
                                                    text=common_senders.get_body(body_input,
                                                                                 body_is_filename=body_is_filename,
                                                                                 path=common_senders.get_message_path())
                                                    .format(**common_senders.get_params_with_candidate(c,
                                                                                                       language_code,
                                                                                                       override_dict)),
                                                    filename=original_body_input if body_is_filename else None)
                                            for c in candidates])

    common.bulk_save(messages)
