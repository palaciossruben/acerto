from django.conf.urls import url

from . import views

app_name = 'api'

urlpatterns = [
    url(r'^get_public_posts$', views.get_public_posts, name='get_public_posts'),
    url(r'^add_messages$', views.add_messages, name='add_messages'),
    url(r'^save_leads$', views.save_leads, name='save_leads'),

    # API v1
    url(r'^v1/register$', views.register, name='register'),
    url(r'^v1/get_work_areas', views.get_work_areas, name='get_work_areas'),
    url(r'^v1/get_cities$', views.get_cities, name='get_cities'),
]
