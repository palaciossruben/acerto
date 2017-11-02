from django.conf.urls import url

from . import views

app_name = 'dashboard'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^campaign/(?P<pk>\d+)$', views.edit_campaign_candidates, name='edit_campaign_candidates'),
    url(r'^test/(?P<pk>\d+)$', views.edit_test, name='test_edit'),
    url(r'^test/new$', views.new_test, name='new_test'),
    url(r'^campaign/new$', views.new_campaign, name='new_campaign'),
    url(r'^campaign/create$', views.create_campaign, name='create_campaign'),
    url(r'^campaign/edit/(?P<pk>\d+)$', views.edit_campaign, name='edit_campaign'),
    url(r'^campaign/interview/(?P<pk>\d+)$', views.interview, name='interview'),
]
