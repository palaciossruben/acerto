from django.conf.urls import url

from business import views

app_name = 'business'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^post$', views.post_index, name='post_index'),
    url(r'^search$', views.search, name='search'),
    url(r'^results$', views.results, name='results'),
    url(r'^form$', views.form, name='form'),
    url(r'^form/post$', views.form_post, name='form_post'),
]
