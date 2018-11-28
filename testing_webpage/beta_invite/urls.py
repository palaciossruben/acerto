from django.conf.urls import url

from . import views

app_name = 'beta_invite'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^registro$', views.register, name='register'),
    url(r'^pruebas$', views.tests, name='tests'),
    url(r'^test[-_]result$', views.get_test_result, name='test_result'),
    url(r'^add[-_]cv$', views.add_cv, name='add_cv'),
    url(r'^add[-_]cv[-_]changes$', views.add_cv_changes),
    url(r'^additional[-_]info$', views.additional_info, name='additional_info'),
    url(r'^save[-_]partial[-_]additional[-_]info$', views.save_partial_additional_info, name='save_partial_additional_info'),
    url(r'^active[-_]campaigns$', views.active_campaigns, name='active_campaigns'),
    url(r'^security[-_]politics$', views.security_politics, name='security_politics'),
    url(r'^apply$', views.apply, name='apply'),
    url(r'^home$', views.home, name='home'),
    url(r'^upload-audio-file$', views.upload_audio_file, name='upload-audio-file'),
]
