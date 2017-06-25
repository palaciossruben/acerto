from django.conf.urls import url
from beta_invite_long_form import views

app_name = 'beta_invite_long_form'

urlpatterns = [
    url(r'^$', views.index, name='index'),
]





