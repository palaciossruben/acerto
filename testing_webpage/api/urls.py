from django.conf.urls import url

from . import views

app_name = 'api'

urlpatterns = [
    url(r'^get_public_posts', views.get_public_posts, name='get_public_posts'),
]
