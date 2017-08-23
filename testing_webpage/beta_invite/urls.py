from django.conf.urls import url

from . import views

app_name = 'beta_invite'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^post$', views.post_index, name='post_index'),
    url(r'^long_form$', views.long_form, name='long_form'),
    url(r'^long_form/post$', views.post_long_form, name='post_long_form'),
    #url(r'^campaigns$', views.post_long_form, name='post_long_form'),
]
