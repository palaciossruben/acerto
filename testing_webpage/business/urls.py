from django.conf.urls import url

from business import views

app_name = 'business'

urlpatterns = [
    url(r'^$', views.index, name='index'),
]
