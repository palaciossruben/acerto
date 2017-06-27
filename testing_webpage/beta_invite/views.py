import os
import smtplib
import unicodedata
from django.core.files.storage import FileSystemStorage
from django.utils.translation import ugettext as _

from django.shortcuts import render
from beta_invite.models import User, Visitor, Profession, EducationLevel, Country
import business
from beta_invite.util import email_sender
from ipware.ip import get_ip
from beta_invite import constants as cts

MAIN_MESSAGE = _("Discover your true passion")
SECONDARY_MESSAGE = _("We search millions of jobs and find the right one for you")


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
    :return: renders a view.
    """

    ip = get_ip(request)

    action_url = '/beta_invite/post'

    Visitor(ip=ip, ui_version=cts.UI_VERSION).save()
    return render(request, cts.BETA_INVITE_VIEW_PATH, {'main_message': MAIN_MESSAGE,
                                                       'secondary_message': SECONDARY_MESSAGE,
                                                       'action_url': action_url,
                                                       })


def post_index(request):
    """
    Action taken when a form is submitted, coming from index.html
    Args:
        request: A request object.

    Returns: saves new User
    """

    ip = get_ip(request)

    user = User(name=request.POST.get('name'),
                email=request.POST.get('email'),
                ip=ip,
                ui_version=cts.UI_VERSION)

    user.save()

    save_curriculum_from_request(request, user)

    # TODO: pay the monthly fee
    #try:
    #    email_sender.send(user, request.LANGUAGE_CODE)
    #except smtplib.SMTPRecipientsRefused:  # cannot send, possibly invalid emails
    #    pass

    return render(request, cts.SUCCESS_VIEW_PATH, {'main_message': MAIN_MESSAGE,
                                                   'secondary_message': SECONDARY_MESSAGE,
                                                   })


# TODO: Localization a las patadas
def translate_list_of_objects(objects, languague_code):
    """Assigns to field name the language specific one."""
    if 'es' in languague_code:
        for o in objects:
            o.name = o.name_es


def long_form(request):
    """
    will render and have the same view as /beta_invite except for message customization.
    """

    ip = get_ip(request)
    action_url = '/beta_invite/long_form/post'
    language_code = request.LANGUAGE_CODE

    professions = Profession.objects.all()
    translate_list_of_objects(professions, language_code)

    education_levels = EducationLevel.objects.all()
    translate_list_of_objects(education_levels, language_code)

    countries = Country.objects.all()

    Visitor(ip=ip, ui_version=cts.UI_VERSION).save()

    return render(request, cts.LONG_FORM_VIEW_PATH, {'main_message': MAIN_MESSAGE,
                                                     'secondary_message': SECONDARY_MESSAGE,
                                                     'action_url': action_url,
                                                     'professions': professions,
                                                     'countries': countries,
                                                     'education_levels': education_levels})


def post_long_form(request):
    """
    Args:
        request: Request object
    Returns: Saves
    """
    ip = get_ip(request)

    profession_id = request.POST.get('profession')
    education_level_id = request.POST.get('education_level')
    country_id = request.POST.get('country')
    experience = request.POST.get('experience')
    age = request.POST.get('age')

    profession = Profession.objects.get(pk=profession_id)
    education_level = EducationLevel.objects.get(pk=education_level_id)
    country = Country.objects.get(pk=country_id)

    user = User(name=request.POST.get('name'),
                email=request.POST.get('email'),
                profession=profession,
                education_level=education_level,
                country=country,
                experience=experience,
                age=age,
                ip=ip,
                ui_version=cts.UI_VERSION)

    user.save()

    save_curriculum_from_request(request, user)

    # TODO: missing santiago@peaku.co credentials.
    #try:
    #    email_sender.send(user)
    #except smtplib.SMTPRecipientsRefused:  # cannot send, possibly invalid emails
    #    pass

    return render(request, cts.SUCCESS_VIEW_PATH, {'main_message': MAIN_MESSAGE,
                                                   'secondary_message': SECONDARY_MESSAGE,
                                                   })
