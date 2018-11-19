from datetime import datetime
from django.contrib.auth import login, authenticate
from django.utils.translation import ugettext as _

import common
from beta_invite.models import User
from beta_invite.util import email_sender
from dashboard.models import Candidate


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


def update_user(campaign, user, user_params, request, signup_form=None):
    """
    Args:
        campaign: campaign
        user: Obj
        user_params: dict with fields of a User obj
        request: HTTP
        signup_form: sign up form, it will add a AuthUser
    Returns: None
    """

    if signup_form:
        add_auth_and_login(signup_form, user, request)

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
    path = common.save_resource_from_request(request, user, field, folder_name)

    if path != '#':
        setattr(user, field, path)
        user.save()


def update_user_with_request(request, user):
    for key, value in request.POST.items():
        if hasattr(User, key):
            value = None if value == '' else value
            setattr(user, key, value)

    user.save()


def add_auth_and_login(signup_form, user, request):

    signup_form.save()
    username = signup_form.cleaned_data.get('username')
    password = signup_form.cleaned_data.get('password1')
    # Creates a Authentication user
    auth_user = authenticate(username=username,
                             password=password)

    # New User pointing to the AuthUser
    user.auth_user = auth_user
    user.save()

    login(request, auth_user)

    return user


def create_user(campaign, user_params, request, is_mobile, signup_form=None):
    """
    Args:
        campaign: obj
        user_params: Dict with user params
        request: HTTP
        is_mobile: Boolean
        signup_form: the form with which it did sign up
    Returns: Creates a new user on the DB.
    """
    user = User(**user_params)
    user.save()  # Saves here to get an id

    if signup_form:
        add_auth_and_login(signup_form, user, request)

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
