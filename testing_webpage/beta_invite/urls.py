from django.conf.urls import url

from . import views

app_name = 'beta_invite'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^servicio_de_empleo$', views.long_form, name='long_form'),
    url(r'^servicio_de_empleo/post$', views.post_long_form, name='post_long_form'),
    url(r'^fast_job$', views.fast_job, name='fast_job'),
    url(r'^fast_job/post$', views.post_fast_job, name='fast_job_post'),
    url(r'^servicio_de_empleo/test_result$', views.get_test_result, name='test_result'),
    url(r'^servicio_de_empleo/interview/(?P<pk>\d+)$', views.interview, name='interview'),
    url(r'^servicio_de_empleo/add_cv$', views.add_cv),
    url(r'^servicio_de_empleo/add_cv_changes$', views.add_cv_changes),
]
