import smtplib
from django.utils.translation import ugettext as _

from django.shortcuts import render
from beta_invite.models import User, Visitor
import business
from beta_invite.util import email_sender
from ipware.ip import get_ip
from beta_invite import constants as cts


def get_error_render(request, error_message, error_params):
    """
    Args:
        request: Request object
        error_message: specific error message
        error_params: dictionary with common params.
    Returns: Renders page with error message.
    """
    error_params['error_message'] = error_message
    return render(request, cts.BETA_INVITE_VIEW_PATH, error_params)


def inner_index(request, is_user_site):
    """
    This view works for both user and business versions. It is displayed on 3 different urls: peaku.co, /business,
    /beta_invite
    :param request: can come with args "name" and "email", if not it will load the initial page.
    :param is_user_site: Boolean indicating the user or business site.
    :return: renders a view.
    """

    ip = get_ip(request)

    if is_user_site:
        user = User(name=request.POST.get('name'),
                    email=request.POST.get('email'),
                    ip=ip,
                    ui_version=cts.UI_VERSION)
    else:
        user = business.models.User(name=request.POST.get('name'),
                                    email=request.POST.get('email'),
                                    ip=ip,
                                    ui_version=cts.UI_VERSION)

    if is_user_site:  # user site
        main_message = _("Discover your true passion")
        secondary_message = _("We search millions of jobs and find the right one for you")
        action_url = '/beta_invite/'
    else:  # business site
        main_message = _("Discover amazing people")
        secondary_message = _("We search millions of profiles and find the ones that best suit your business")
        action_url = '/business/'

    # first time loading
    if user.name is None or user.email is None:

        if is_user_site:
            Visitor(ip=ip, ui_version=cts.UI_VERSION).save()
        else:
            business.models.Visitor(ip=ip, ui_version=cts.UI_VERSION).save()

        return render(request, cts.BETA_INVITE_VIEW_PATH, {'main_message': main_message,
                                                           'secondary_message': secondary_message,
                                                           'action_url': action_url,
                                                           'missing_name_alert': _("Missing name."),
                                                           'missing_email_alert': _("Missing email."),
                                                           'invalid_email_alert': _("Make sure you include a valid email.")})

    user.save()
    # TODO: deactivated until fixed on production.
    #try:
    #    email_sender.send(user)
    #except smtplib.SMTPRecipientsRefused:  # cannot send, possibly invalid emails
    #    return render(request, cts.BETA_INVITE_VIEW_PATH, {
    #        'error_message': _("Cannot send confirmation email, please check it."),
    #        })

    return render(request, cts.BETA_INVITE_VIEW_PATH, {'successful_message': _("Successful submission :)"),
                                                       'main_message': main_message,
                                                       'secondary_message': secondary_message,
                                                       'action_url': action_url,
                                                       'missing_name_alert': _("Missing name."),
                                                       'missing_email_alert': _("Missing email."),
                                                       'invalid_email_alert': _("Make sure you include a valid email.")})


def index(request):
    return inner_index(request, is_user_site=True)
