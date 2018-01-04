from django.conf.urls import url

from . import views

app_name = 'dashboard'

urlpatterns = [
    url(r'^$', views.index, name='index'),

    # Campaign
    url(r'^campaign/(?P<pk>\d+)$', views.edit_campaign_candidates, name='edit_campaign_candidates'),
    url(r'^campaign/new$', views.new_campaign, name='new_campaign'),
    url(r'^campaign/create$', views.create_campaign, name='create_campaign'),
    url(r'^campaign/edit/(?P<pk>\d+)$', views.edit_campaign, name='edit_campaign'),
    url(r'^campaign/update_basic_properties$', views.update_basic_properties),

    # Campaign tests
    url(r'^campaign/(?P<pk>\d+)/add_test$', views.add_test),
    url(r'^campaign/(?P<pk>\d+)/delete_test$', views.delete_test),
    url(r'^campaign/(?P<pk>\d+)/tests$', views.tests),


    # Test
    url(r'^test/(?P<pk>\d+)$', views.edit_test, name='test_edit'),
    url(r'^test/new$', views.new_test, name='new_test'),

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
]
