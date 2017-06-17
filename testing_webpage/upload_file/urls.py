from django.conf.urls import url

from . import views

app_name = 'upload_file'

urlpatterns = [
    url(r'^$', views.simple_upload, name='simple_upload'),
]
