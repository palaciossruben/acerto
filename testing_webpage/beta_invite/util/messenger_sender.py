"""
Sends messages.
"""
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

    for candidate in candidates:

        params = common_senders.get_params_with_candidate(candidate, language_code, override_dict)
        body = common_senders.get_body(body_input,
                                       body_is_filename=body_is_filename,
                                       path=common_senders.get_message_path())
        m = Message(candidate=candidate, text=body.format(**params))
        if body_is_filename:
            m.filename = original_body_input
        m.save()
