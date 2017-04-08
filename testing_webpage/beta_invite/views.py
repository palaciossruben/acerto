import smtplib
from django.utils.translation import ugettext as _

from django.shortcuts import render
from beta_invite.models import User, Visitor
from beta_invite.util import email_sender
from ipware.ip import get_ip
from beta_invite import constants as cts
from user_agents import parse


def is_email_valid(email):
    """
    Simple logic won't bother here
    :param email: string
    :return: boolean
    """
    return '@' in email and '.' in email


def is_string_valid(any_string):
    """
    Validate all fields available.
    :param any_string: string, cannot be null or empty
    :return: boolean
    """
    return any_string is not None and any_string != ''


def get_error_render(request, user, error_message, is_desktop):

    return render(request, cts.BETA_INVITE_VIEW_PATH, {
            'error_message': error_message,
            'name': user.name,
            'email': user.email,
            'is_desktop': is_desktop,
        })


def index(request):
    """
    :param request: can come with args "name" and "email", if not it will load the initial page.
    :return: renders a view.
    """

    ua_string = request.META['HTTP_USER_AGENT']
    user_agent = parse(ua_string)
    is_desktop = not user_agent.is_mobile

    ip = get_ip(request)
    user = User(name=request.POST.get('name'),
                email=request.POST.get('email'),
                ip=ip,
                ui_version=cts.UI_VERSION)

    # first time loading. Fields have no value yet.
    if user.name is None or user.email is None:
        Visitor(ip=ip, ui_version=cts.UI_VERSION).save()
        return render(request, cts.BETA_INVITE_VIEW_PATH, {'is_desktop': is_desktop})

    if is_string_valid(user.name):

        if is_string_valid(user.email):

            if is_email_valid(user.email):
                user.save()
                # TODO: deactivated until fixed on production.
                #try:
                #    email_sender.send(user)
                #except smtplib.SMTPRecipientsRefused:  # cannot send, possibly invalid emails
                #    return render(request, cts.BETA_INVITE_VIEW_PATH, {
                #        'error_message': _("Cannot send confirmation email, please check it."),
                #        })

                return render(request, cts.BETA_INVITE_VIEW_PATH, {
                    'successful_message': _("Successful submission :)"),
                    'is_desktop': is_desktop})
            else:
                return get_error_render(request, user, _("Make sure you include a valid email."), is_desktop)
        else:
            return get_error_render(request, user, _("Missing email."), is_desktop)
    else:
        return get_error_render(request, user, _("Missing name."), is_desktop)
