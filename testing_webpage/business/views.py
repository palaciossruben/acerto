from ipware.ip import get_ip
from django.shortcuts import render
from django.utils.translation import ugettext as _

import business
from business import constants as cts


def index(request):
    """
    will render and have the same view as /beta_invite except for message customization.
    """

    ip = get_ip(request)

    business_user = business.models.User(name=request.POST.get('name'),
                                         email=request.POST.get('email'),
                                         ip=ip,
                                         ui_version=cts.UI_VERSION)

    main_message = _("Discover amazing people")
    secondary_message = _("We search millions of profiles and find the ones that best suit your business")
    action_url = '/business/'

    # first time loading
    if business_user.name is None or business_user.email is None:
        business.models.Visitor(ip=ip, ui_version=cts.UI_VERSION).save()

        return render(request, cts.BUSINESS_VIEW_PATH, {'main_message': main_message,
                                                        'secondary_message': secondary_message,
                                                        'action_url': action_url,
                                                        })

    business_user.save()

    # TODO: pay the monthly fee
    #try:
    #    email_sender.send(user, request.LANGUAGE_CODE)
    #except smtplib.SMTPRecipientsRefused:  # cannot send, possibly invalid emails
    #    pass

    return render(request, cts.SUCCESS_VIEW_PATH, {'main_message': main_message,
                                                   'secondary_message': secondary_message,
                                                   })
