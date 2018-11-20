from testing_webpage import constants as cts
from beta_invite.models import Campaign, WorkAreaSegment
from business.models import BusinessUser
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import logout

from beta_invite.models import User
from beta_invite import test_module
from dashboard.models import Candidate


def index(request):
    """
    will render the intro
    """
    return render(request, cts.INDEX_VIEW_PATH)


def sitemap(request):
    return render(request, 'testing_webpage/sitemap.xml', {}, content_type="application/xhtml+xml")


def bing_site_auth(request):
    return render(request, 'testing_webpage/BingSiteAuth.xml', {}, content_type="application/xhtml+xml")


def robots(request):
    return render(request, 'testing_webpage/robots.txt', {}, content_type="application/xhtml+txt")


def add_missing_tests(user, campaigns):
    if user:
        for campaign in campaigns:
            prospective_candidate = Candidate(user=user, campaign=campaign)
            campaign.passed_tests = [s.test for s in test_module.get_high_scores(prospective_candidate)]
            campaign.missing_tests = test_module.get_missing_tests(prospective_candidate)


def jobs(request):
    code = request.GET.get('segment_code')
    user = User.get_user_from_request(request)

    try:
        segment = WorkAreaSegment.objects.get(code=code)
        campaigns = Campaign.objects.filter(~Q(title_es=None),
                                            state__code__in=['I', 'A'],
                                            removed=False,
                                            work_area__segment__code=segment.code)
        if len(campaigns) > 0:
            active_campaigns = campaigns
        else:
            active_campaigns = Campaign.objects.filter(~Q(title_es=None),
                                                       state__code__in=['I', 'A'],
                                                       removed=False)

        add_missing_tests(user, active_campaigns)
        return render(request, cts.JOBS_VIEW_PATH, {'active_campaigns': active_campaigns})

    except ObjectDoesNotExist:
        active_campaigns = Campaign.objects.filter(~Q(title_es=None),
                                                   state__code__in=['I', 'A'],
                                                   removed=False)
        add_missing_tests(user, active_campaigns)
        return render(request, cts.JOBS_VIEW_PATH, {'active_campaigns': active_campaigns})


@login_required
def home(request):
    """
    This is a general login for home, can redirect to business_home
    :param request:
    :return:
    """

    if BusinessUser.get_business_user(request.user):
        return redirect('business:home')
    else:  # its a candidate user
        return render(request, 'testing_webpage/home.html')


def my_logout(request):
    if BusinessUser.get_business_user(request.user):
        logout(request)
        return redirect('business:index')
    else:  # its a candidate user
        logout(request)
        return redirect('jobs')
