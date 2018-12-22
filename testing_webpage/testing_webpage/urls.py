"""testing_webpage URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url('^', include('django.contrib.auth.urls')),
    url(r'^servicio-de-empleo/', include('beta_invite.urls')),
    url(r'^seleccion-de-personal/', include('business.urls')),
    url(r'^dashboard/', include('dashboard.urls')),
    url(r'^api/', include('api.urls')),
    url(r'^oauth/', include('social_django.urls', namespace='social')),
    url(r'^cv/', include('nice.urls')),

    url(r'^$', views.index, name='index'),
    url(r'^trabajos$', views.jobs, name='jobs'),
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^my[-_]logout$', views.my_logout, name='logout'),
    url(r'^home[-_]test$', views.home, name='home'),
]

urlpatterns += i18n_patterns(
    url(r'^staffing$', views.index, name='index'),
    url(r'^sitemap.xml$', views.sitemap, name='sitemap'),
    url(r'^BingSiteAuth.xml$', views.bing_site_auth, name='BingSiteAuth'),
    url(r'^robots.txt$', views.robots, name='robots')
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
