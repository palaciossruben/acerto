from django.conf.urls import url

from . import views

app_name = 'nice'

urlpatterns = [
    url(r'^(?P<candidate_id>\d+)$', views.cv_test, name='cv_test'),
    url(r'^(?P<candidate_id>\d+)/download$', views.download_cv, name='download_cv'),
]
