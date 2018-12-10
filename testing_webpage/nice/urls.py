from django.conf.urls import url

from . import views

app_name = 'nice'

urlpatterns = [
    url(r'^$', views.cv_test, name='cv_test'),
]
