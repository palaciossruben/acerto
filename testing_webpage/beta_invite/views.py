from django.shortcuts import render
from beta_invite.models import User, Visitor
from beta_invite.util import email_sender
from ipware.ip import get_ip


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


def get_error_render(request, user, error_message):

    return render(request, 'beta_invite/index.html', {
            'error_message': error_message,
            'name': user.name,
            'email': user.email,
        })


def index(request):
    """
    :param request: can come with args "name" and "email", if not it will load the initial page.
    :return: renders a view.
    """

    ip = get_ip(request)
    user = User(name=request.POST.get('name'), email=request.POST.get('email'), ip=ip)

    # first time loading. Fields have no value yet.
    if user.name is None or user.email is None:
        Visitor(ip=ip).save()
        return render(request, 'beta_invite/index.html', {})

    if is_string_valid(user.name):

        if is_string_valid(user.email):

            if is_email_valid(user.email):
                user.save()
                email_sender.send(user)
                return render(request, 'beta_invite/index.html', {
                    'successful_message': "Successful submission, you will receive an email shortly :)",
                })
            else:
                return get_error_render(request, user, "Make sure you include a valid email.")
        else:
            return get_error_render(request, user, "Missing email.")
    else:
        return get_error_render(request, user, "Missing name.")
