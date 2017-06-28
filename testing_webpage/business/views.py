from ipware.ip import get_ip
from django.shortcuts import render
from django.utils.translation import ugettext as _

import business
import beta_invite
from business import constants as cts
from beta_invite.models import User, EducationLevel

MAIN_MESSAGE = "Discover amazing people"
SECONDARY_MESSAGE = "We search millions of profiles and find the ones that best suit your business"


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
    return render(request, cts.BUSINESS_VIEW_PATH, {'main_message': _(MAIN_MESSAGE),
                                                    'secondary_message': _(SECONDARY_MESSAGE),
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

    return render(request, cts.SUCCESS_VIEW_PATH, {'main_message': _(MAIN_MESSAGE),
                                                   'secondary_message': _(SECONDARY_MESSAGE),
                                                   })


def search(request):
    """
    will render the search view.
    Args:
        request: Object
    Returns: Save
    """

    ip = get_ip(request)
    action_url = '/business/results'

    countries, education_levels, professions = beta_invite.views.get_drop_down_values(request.LANGUAGE_CODE)

    business.models.Visitor(ip=ip, ui_version=cts.UI_VERSION).save()
    return render(request, cts.SEARCH_VIEW_PATH, {'main_message': _(MAIN_MESSAGE),
                                                  'secondary_message': _(SECONDARY_MESSAGE),
                                                  'action_url': action_url,
                                                  'countries': countries,
                                                  'education_levels': education_levels,
                                                  'professions': professions,
                                                  })


def get_matching_users(request):
    """
    Simple DB matching between criteria and DB.
    Args:
        request: Request obj
    Returns: List with matching Users
    """

    profession_id = request.POST.get('profession')
    education_level_id = request.POST.get('education_level')
    education_level = EducationLevel.objects.get(pk=education_level_id)
    country_id = request.POST.get('country')
    experience = request.POST.get('experience')

    # TODO: missing education level
    return User.objects.filter(country_id=country_id)\
        .filter(profession_id=profession_id)\
        .filter(experience__gte=experience)


def results(request):
    """
    Args:
        request: Request object
    Returns: renders results.html view.
    """

    users = get_matching_users(request)

    return render(request, cts.RESULTS_VIEW_PATH, {'main_message': _(MAIN_MESSAGE),
                                                   'secondary_message': _(SECONDARY_MESSAGE),
                                                   'users': users,
                                                   })
