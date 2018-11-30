from django.conf.urls import url

from . import views
from . import stats

app_name = 'dashboard'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # All tests
    url(r'^tests_list$', views.tests_list, name='tests_list'),

    # Campaign
    url(r'^campaign/(?P<campaign_id>\d+)$', views.edit_campaign_candidates, name='campaign'),
    url(r'^campaign/new$', views.new_campaign, name='new_campaign'),
    url(r'^campaign/create$', views.create_campaign, name='create_campaign'),
    url(r'^campaign/edit/(?P<pk>\d+)$', views.edit_campaign, name='edit_campaign'),
    url(r'^campaign/update[-_]basic[-_]properties$', views.update_basic_properties),
    url(r'^campaign/delete/(?P<pk>\d+)$', views.delete_campaign, name='delete_campaign'),
    url(r'^campaign/candidate/(?P<candidate_id>\d+)$', views.candidate_detail, name='candidate_detail'),

    # Campaign tests
    url(r'^campaign/(?P<pk>\d+)/add[-_]test$', views.add_test),
    url(r'^campaign/(?P<pk>\d+)/delete[-_]test$', views.delete_test),
    url(r'^campaign/(?P<pk>\d+)/tests$', views.tests),

    # Test
    # url(r'^', include('home.urls', namespace='home')),
    url(r'^test/(?P<pk>\d+)$', views.edit_test, name='test_edit'),
    url(r'^test/new$', views.new_test, name='new_test'),
    url(r'^test/save$', views.save_test, name='save_test'),
    url(r'^test/update/(?P<pk>\d+)$', views.update_test, name='update_test'),
    url(r'^test/delete[-_]question$', views.delete_question, name='delete_question'),
    url(r'^test/delete[-_]answer$', views.delete_answer, name='delete_answer'),
    url(r'^test/duplicate/(?P<pk>\d+)$', views.duplicate_test, name='duplicate_test'),

    # Bullets
    url(r'^campaign/(?P<pk>\d+)/bullets$', views.bullets),
    url(r'^campaign/update[-_]bullets$', views.update_bullets),
    url(r'^campaign/delete[-_]bullet$', views.delete_bullet),

    # Interview
    url(r'^edit[-_]intro[-_]video$', views.edit_intro_video, name='edit_intro_video'),
    url(r'^campaign/interview/(?P<pk>\d+)$', views.interview, name='interview'),
    url(r'^campaign/check_interview$', views.check_interview, name='check_interview'),
    url(r'^campaign/interview/create[-_]interview[-_]question$', views.create_interview_question, name='create_interview_question'),
    url(r'^campaign/interview/update[-_]interview[-_]question$', views.update_interview_question, name='update_interview_question'),
    url(r'^campaign/interview/delete[-_]interview[-_]question$', views.delete_interview_question, name='delete_interview_question'),

    # Auto messenger
    url(r'^send[-_]new[-_]contacts$', views.send_new_contacts, name='send_new_contacts'),
    url(r'^send[-_]messages$', views.send_messages, name='send_messages'),

    # stats
    url(r'^candidates[-_]stats$', stats.candidates_count, name='candidates_stats'),
    url(r'^campaign[-_]stats$', stats.campaign_count, name='campaign_stats'),
    url(r'^number[-_]of[-_]forecasts$', stats.number_of_forecasts, name='number_of_forecasts'),
    url(r'^positive[-_]forecasts$', stats.positive_forecasts, name='positive_forecasts'),
    url(r'^negative[-_]forecasts$', stats.negative_forecasts, name='negative_forecasts'),
    url(r'^candidates[-_]per[-_]user$', stats.candidates_per_user, name='candidates_per_user'),
    url(r'^candidates[-_]from[-_]old[-_]users$', stats.candidates_from_old_users, name='candidates_from_old_users'),
    url(r'^stuck[-_]candidates$', stats.stuck_candidates, name='stuck_candidates'),
    url(r'^recommended[-_]candidates$', stats.recommended_candidates, name='recommended_candidates'),
    url(r'^paid-campaign-registrations$', stats.get_paid_campaign_registrations, name='paid_campaign_registrations'),
    url(r'^unique-users-registrations$', stats.get_unique_users_registrations, name='unique_users_registrations'),
]
