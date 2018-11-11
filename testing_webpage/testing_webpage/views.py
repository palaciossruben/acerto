from django.shortcuts import render
from testing_webpage import constants as cts
from beta_invite.models import Campaign, WorkAreaSegment
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist


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


def jobs(request):
    code = request.GET.get('segment_code')

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
        return render(request, cts.JOBS_VIEW_PATH, {'active_campaigns': active_campaigns})

    except ObjectDoesNotExist:
        return render(request, cts.JOBS_VIEW_PATH, {'active_campaigns': Campaign.objects.filter(~Q(title_es=None),
                                                                                                state__code__in=['I', 'A'],
                                                                                                removed=False)})