from beta_invite import views as beta_views

from django.utils.translation import ugettext as _

from django.shortcuts import render
from beta_invite.models import User, Visitor, Profession, EducationLevel, Country
from ipware.ip import get_ip
from beta_invite_long_form import constants as cts
from beta_invite import constants as beta_invite_cts

MAIN_MESSAGE = _("Discover your true passion")
SECONDARY_MESSAGE = _("We search millions of jobs and find the right one for you")


# TODO: Localization a las patadas
def translate_list_of_objects(objects, languague_code):
    """Assigns to field name the language specific one."""
    if 'es' in languague_code:
        for o in objects:
            o.name = o.name_es


def index(request):
    """
    will render and have the same view as /beta_invite except for message customization.
    """

    ip = get_ip(request)
    action_url = '/beta_invite_long_form/post'
    language_code = request.LANGUAGE_CODE

    professions = Profession.objects.all()
    translate_list_of_objects(professions, language_code)

    education_levels = EducationLevel.objects.all()
    translate_list_of_objects(education_levels, language_code)

    countries = Country.objects.all()

    Visitor(ip=ip, ui_version=cts.UI_VERSION).save()

    return render(request, cts.BETA_INVITE_LONG_FORM_VIEW_PATH, {'main_message': MAIN_MESSAGE,
                                                                 'secondary_message': SECONDARY_MESSAGE,
                                                                 'action_url': action_url,
                                                                 'professions': professions,
                                                                 'countries': countries,
                                                                 'education_levels': education_levels})


def post_index(request):
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

    beta_views.save_curriculum_from_request(request, user)

    # TODO: missing santiago@peaku.co credentials.
    #try:
    #    email_sender.send(user)
    #except smtplib.SMTPRecipientsRefused:  # cannot send, possibly invalid emails
    #    pass

    return render(request, beta_invite_cts.SUCCESS_VIEW_PATH, {'main_message': MAIN_MESSAGE,
                                                               'secondary_message': SECONDARY_MESSAGE,
                                                               })
