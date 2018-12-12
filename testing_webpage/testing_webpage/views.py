from testing_webpage import constants as cts
from beta_invite.models import Campaign
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

    # TODO: redirects to home of each candidate, but is not working well!!!
    """
    if BusinessUser.get_business_user(request.user):
        return redirect('business:home')
    elif User.get_user_from_request(request):  # it its a candidate user
        return redirect('jobs')
    """

    return render(request, cts.INDEX_VIEW_PATH)


def sitemap(request):
    return render(request, 'testing_webpage/sitemap.xml', {}, content_type="application/xhtml+xml")


def bing_site_auth(request):
    return render(request, 'testing_webpage/BingSiteAuth.xml', {}, content_type="application/xhtml+xml")


def robots(request):
    return render(request, 'testing_webpage/robots.txt', {}, content_type="application/xhtml+txt")


def add_missing_tests(user, campaigns):
    """
    Will add to temp properties to the campaigns, in order to show tests that are completed or missing
    :param user:
    :param campaigns:
    :return:
    """
    if user:
        for campaign in campaigns:
            prospective_candidate = Candidate(user=user, campaign=campaign)
            high_scores = test_module.get_high_scores(prospective_candidate, campaign)
            campaign.passed_tests = [s.test for s in high_scores]
            campaign.missing_tests = test_module.get_missing_tests(prospective_candidate,
                                                                   campaign,
                                                                   high_scores=high_scores)


def get_segment_code(request, user):
    code = request.GET.get('segment_code')

    if user and code is None:
        segment = user.get_work_area_segment()
        if segment:
            return segment.code

    return code


def jobs(request):
    user = User.get_user_from_request(request)
    segment_code = get_segment_code(request, user)

    try:
        campaigns = Campaign.objects.filter(~Q(title_es=None),
                                            state__code__in=['A'],
                                            removed=False,
                                            work_area__segment__code=segment_code)
        if len(campaigns) > 0:
            active_campaigns = campaigns
        else:
            active_campaigns = Campaign.objects.filter(~Q(title_es=None),
                                                       state__code__in=['A'],
                                                       removed=False)

        add_missing_tests(user, active_campaigns)

        half = int(len(active_campaigns)/2)
        left_campaigns = active_campaigns[:half]
        right_campaigns = active_campaigns[half:]

        return render(request, cts.JOBS_VIEW_PATH, {'left_campaigns': left_campaigns,
                                                    'right_campaigns': right_campaigns})

    except ObjectDoesNotExist:
        active_campaigns = Campaign.objects.filter(~Q(title_es=None),
                                                   state__code__in=['A'],
                                                   removed=False)
        add_missing_tests(user, active_campaigns)
        half = int(len(active_campaigns)/2)
        left_campaigns = active_campaigns[:half]
        right_campaigns = active_campaigns[half:]

        return render(request, cts.JOBS_VIEW_PATH, {'left_campaigns': left_campaigns,
                                                    'right_campaigns': right_campaigns})


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
