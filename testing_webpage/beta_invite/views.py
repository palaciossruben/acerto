import os
import smtplib
import unicodedata
from django.core.files.storage import FileSystemStorage
from django.utils.translation import ugettext as _

from django.shortcuts import render
from beta_invite.models import User, Visitor
import business
from beta_invite.util import email_sender
from ipware.ip import get_ip
from beta_invite import constants as cts


def remove_accents(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')


def save_curriculum_from_request(request, user):
    """
    Saves file on machine resumes/* file system
    Args:
        request: HTTP request
    Returns: None, just saves file.
    """

    # validate correct method and has file.
    if request.method == 'POST' and len(request.FILES) != 0:

        curriculum_file = request.FILES['curriculum']
        fs = FileSystemStorage()

        # TODO: make this dynamic
        user_id_folder = str(user.id)
        folder = os.path.join('subscribe/resumes', user_id_folder)

        # create file path:
        if not os.path.isdir(folder):
            os.mkdir(folder)

        file_path = os.path.join(folder, remove_accents(curriculum_file.name))

        fs.save(file_path, curriculum_file)


def index(request):
    """
    This view works for both user and business versions. It is displayed on 3 different urls: peaku.co, /business,
    /beta_invite
    :param request: can come with args "name" and "email", if not it will load the initial page.
    :param is_user_site: Boolean indicating the user or business site.
    :return: renders a view.
    """

    ip = get_ip(request)

    user = User(name=request.POST.get('name'),
                email=request.POST.get('email'),
                ip=ip,
                ui_version=cts.UI_VERSION)

    main_message = _("Discover your true passion")
    secondary_message = _("We search millions of jobs and find the right one for you")
    action_url = '/beta_invite/'

    # first time loading
    if user.name is None or user.email is None:
        Visitor(ip=ip, ui_version=cts.UI_VERSION).save()
        return render(request, cts.BETA_INVITE_VIEW_PATH, {'main_message': main_message,
                                                           'secondary_message': secondary_message,
                                                           'action_url': action_url,
                                                           })

    user.save()

    save_curriculum_from_request(request, user)

    # TODO: pay the monthly fee
    #try:
    #    email_sender.send(user, request.LANGUAGE_CODE)
    #except smtplib.SMTPRecipientsRefused:  # cannot send, possibly invalid emails
    #    pass

    return render(request, cts.SUCCESS_VIEW_PATH, {'main_message': main_message,
                                                   'secondary_message': secondary_message,
                                                   })
