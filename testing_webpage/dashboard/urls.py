from django.conf.urls import url

from . import views

app_name = 'beta_invite'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^campaign_candidate_edit/(?P<pk>\d+)$', views.campaign_candidate_edit, name='campaign_candidate_edit'),
    #url(r'^post$', views.post_index, name='post_index'),
    #url(r'^long_form$', views.long_form, name='long_form'),
    #url(r'^long_form/post$', views.post_long_form, name='post_long_form'),
    #url(r'^fast_job$', views.fast_job, name='fast_job'),
    #url(r'^fast_job/post$', views.post_fast_job, name='fast_job_post'),
]
