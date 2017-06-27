from ipware.ip import get_ip
from django.shortcuts import render
from django.utils.translation import ugettext as _

import business
from business import constants as cts

MAIN_MESSAGE = _("Discover amazing people")
SECONDARY_MESSAGE = _("We search millions of profiles and find the ones that best suit your business")


def index(request):
    """
    will render and have the same view as /beta_invite except for message customization.
    Args:
        request: Object
    Returns: Save
    """

    ip = get_ip(request)
    action_url = '/business/post'

    business.models.Visitor(ip=ip, ui_version=cts.UI_VERSION).save()
    return render(request, cts.BUSINESS_VIEW_PATH, {'main_message': MAIN_MESSAGE,
                                                    'secondary_message': SECONDARY_MESSAGE,
                                                    'action_url': action_url,
                                                    })


def post_index(request):
    """
    Saves model to DB
    Args:
        request:

    Returns: Saves
    """
    ip = get_ip(request)
    business_user = business.models.User(name=request.POST.get('name'),
                                         email=request.POST.get('email'),
                                         ip=ip,
                                         ui_version=cts.UI_VERSION)
    business_user.save()

    # TODO: pay the monthly fee
    #try:
    #    email_sender.send(user, request.LANGUAGE_CODE)
    #except smtplib.SMTPRecipientsRefused:  # cannot send, possibly invalid emails
    #    pass

    return render(request, cts.SUCCESS_VIEW_PATH, {'main_message': MAIN_MESSAGE,
                                                   'secondary_message': SECONDARY_MESSAGE,
                                                   })
