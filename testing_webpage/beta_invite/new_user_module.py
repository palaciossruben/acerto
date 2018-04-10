import os
import subprocess
import unicodedata
from datetime import datetime

from django.core.files.storage import FileSystemStorage
from django.utils.translation import ugettext as _

from beta_invite.models import User
from beta_invite.util import email_sender
from dashboard.models import Candidate
import common


def remove_accents(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')


def rename_filename(filename):
    """Removes accents, spaces and other chars to have a easier time later"""

    replacement = {' ': '_', '(': '_', ')': '_'}

    for my_char, replace_char in replacement.items():

        if my_char in filename:
            filename = filename.replace(my_char, replace_char)

    return remove_accents(filename)


def save_resource_from_request(request, user, param_name, folder_name):
    """
    Saves file on machine resumes/* file system
    Args:
        request: HTTP request
        user: Object
        param_name: string, name of File on the request
    Returns: file url or None if nothing is saves.
    """

    # validate correct method and has file.
    if request.method == 'POST' and len(request.FILES) != 0 and request.FILES.get(param_name) is not None:

        my_file = request.FILES[param_name]
        fs = FileSystemStorage()

        user_id_folder = str(user.id)

        folder = os.path.join(folder_name, user_id_folder)

        file_path = os.path.join(folder, rename_filename(my_file.name))

        fs.save(file_path, my_file)

        # once saved it will collect the file
        subprocess.call('python3 manage.py collectstatic -v0 --noinput', shell=True)

        # at last returns the curriculum url
        return file_path

    else:
        return '#'


def user_if_exists(email, phone, campaign):
    """
    Args:
        email: string
    Returns: The most recent user if exists, else None
    """

    # Uses email as unique id
    if campaign.has_email:
        for u in User.objects.filter(email=email).order_by('-created_at'):
            return u
    else:  # uses phone as unique id
        for u in User.objects.filter(phone=phone).order_by('-created_at'):
            return u


def candidate_if_exists(campaign, user):
    """
    Args:
        campaign: obj
        user: obj
    Returns: The most recent user if exists, else None
    """
    for c in Candidate.objects.filter(campaign=campaign, user=user).order_by('-created_at'):
        return c


def update_user(campaign, user, user_params, request):
    """
    Args:
        user: Obj
        user_params: dict with fields of a User obj
        request: HTTP
    Returns: None
    """

    common.update_object(user, user_params)
    user.updated_at = datetime.utcnow()
    user.save()

    update_resource(request, user, 'curriculum_url', 'resumes')
    update_resource(request, user, 'photo_url', 'candidate_photo')
    update_resource(request, user, 'brochure_url', 'candidate_brochure')

    candidate = candidate_if_exists(campaign, user)
    if not candidate:
        Candidate(campaign=campaign, user=user).save()

    return user


def update_resource(request, user, field, folder_name):
    path = save_resource_from_request(request, user, field, folder_name)

    if path != '#':
        setattr(user, field, path)
        user.save()


def update_user_with_request(request, user):
    for key, value in request.POST.items():
        if hasattr(User, key):
            setattr(user, key, value)

    user.save()


def create_user(campaign, user_params, request, is_mobile):
    """
    Args:
        campaign: obj
        user_params: Dict with user params
        request: HTTP
        is_mobile: Boolean
    Returns: Creates a new user on the DB.
    """
    user = User(**user_params)
    # Saves here to get an id
    # Saves here to get an id
    user.save()

    update_resource(request, user, 'curriculum_url', 'resumes')
    user.save()

    # Starts on Backlog default state, when no evaluation has been done.
    candidate = Candidate(campaign=campaign, user=user)
    candidate.save()

    email_body_name = 'user_signup_email_body'
    if is_mobile:
        email_body_name += '_mobile'

    email_sender.send(objects=candidate,
                      language_code=request.LANGUAGE_CODE,
                      body_input=email_body_name,
                      subject=_('Welcome to PeakU'))

    return user
