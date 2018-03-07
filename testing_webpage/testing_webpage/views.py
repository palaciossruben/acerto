from django.shortcuts import render
from testing_webpage import constants as cts


def index(request):
    """
    will render the intro
    """
    return render(request, cts.INDEX_VIEW_PATH)


def sitemap(request):
    return render(request, 'testing_webpage/sitemap.xml', {}, content_type="application/xhtml+xml")
