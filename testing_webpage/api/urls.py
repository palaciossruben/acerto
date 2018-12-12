from django.conf.urls import url

from . import views

app_name = 'api'

urlpatterns = [
    url(r'^get[-_]public[-_]posts$', views.get_public_posts, name='get_public_posts'),
    url(r'^add[-_]messages$', views.add_messages, name='add_messages'),
    url(r'^save[-_]leads$', views.save_leads, name='save_leads'),
    url(r'^get[-_]leads[-_]to[-_]filter$', views.get_leads_to_filter, name='get_leads_to_filter'),
    url(r'^get[-_]domains[-_]to[-_]filter$', views.get_domains_to_filter, name='get_domains_to_filter'),

    # API v1
    url(r'^v1/register$', views.register, name='register'),
    url(r'^v1/get[-_]work[-_]areas', views.get_work_areas, name='get_work_areas'),
    url(r'^v1/get[-_]cities$', views.get_cities, name='get_cities'),
    url(r'^v1/get[-_]campaigns$', views.get_campaigns, name='get_campaigns'),
]
