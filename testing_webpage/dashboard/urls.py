from django.conf.urls import url

from . import views
from . import stats

app_name = 'dashboard'

urlpatterns = [
    url(r'^$', views.index, name='index'),

    # Campaign
    url(r'^campaign/(?P<pk>\d+)$', views.edit_campaign_candidates, name='edit_campaign_candidates'),
    url(r'^campaign/new$', views.new_campaign, name='new_campaign'),
    url(r'^campaign/create$', views.create_campaign, name='create_campaign'),
    url(r'^campaign/edit/(?P<pk>\d+)$', views.edit_campaign, name='edit_campaign'),
    url(r'^campaign/update_basic_properties$', views.update_basic_properties),
    url(r'^business_dashboard/(?P<pk>\d+)\?{0,1}.*$', views.business_dashboard, name='business_dashboard'),

    # Campaign tests
    url(r'^campaign/(?P<pk>\d+)/add_test$', views.add_test),
    url(r'^campaign/(?P<pk>\d+)/delete_test$', views.delete_test),
    url(r'^campaign/(?P<pk>\d+)/tests$', views.tests),

    # Test
    #url(r'^', include('home.urls', namespace='home')),
    url(r'^test/(?P<pk>\d+)$', views.edit_test, name='test_edit'),
    url(r'^test/new$', views.new_test, name='new_test'),
    url(r'^test/save$', views.save_test, name='save_test'),
    url(r'^test/update/(?P<pk>\d+)$', views.update_test, name='update_test'),

    # Bullets
    url(r'^campaign/(?P<pk>\d+)/bullets$', views.bullets),
    url(r'^campaign/update_bullets$', views.update_bullets),
    url(r'^campaign/delete_bullet$', views.delete_bullet),

    # Interview
    url(r'^edit_intro_video$', views.edit_intro_video, name='edit_intro_video'),
    url(r'^campaign/interview/(?P<pk>\d+)$', views.interview, name='interview'),
    url(r'^campaign/check_interview$', views.check_interview, name='check_interview'),
    url(r'^campaign/interview/create_interview_question$', views.create_interview_question, name='create_interview_question'),
    url(r'^campaign/interview/update_interview_question$', views.update_interview_question, name='update_interview_question'),
    url(r'^campaign/interview/delete_interview_question$', views.delete_interview_question, name='delete_interview_question'),

    # Auto messenger
    url(r'^send_new_contacts$', views.send_new_contacts, name='send_new_contacts'),
    url(r'^send_messages$', views.send_messages, name='send_messages'),

    # stats
    url(r'^candidates_stats$', stats.candidates_count, name='candidates_stats'),
    url(r'^campaign_stats$', stats.campaigns_count, name='campaign_stats'),
]
