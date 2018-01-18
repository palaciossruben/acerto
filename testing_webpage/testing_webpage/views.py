from beta_invite import views as beta_views
from django.shortcuts import render


def index(request):
    """
    will render and have the same view as /beta_invite
    """
    return beta_views.index(request)


def sitemap(request):

    return render(request, 'testing_webpage/sitemap.xml', {}, content_type="application/xhtml+xml")
