from django.shortcuts import render
from testing_webpage import constants as cts
from beta_invite.models import Campaign


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
    segment_code = request.GET.get('segment_code')
    if segment_code is None:  # if code not found will return everything
        return render(request, cts.JOBS_VIEW_PATH,
                      {'active_campaigns': Campaign.objects.filter(state__code__in=['I', 'A'])})
    else:
        return render(request, cts.JOBS_VIEW_PATH,
                      {'active_campaigns': Campaign.objects.filter(state__code__in=['I', 'A'],
                                                                   work_area__segment__code=segment_code)})
