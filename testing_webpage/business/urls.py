from django.conf.urls import url
from django.contrib.auth import views as auth_views

from business import views

app_name = 'business'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^post$', views.post_index, name='post_index'),
    url(r'^search$', views.search, name='search'),
    url(r'^results$', views.results, name='results'),
    url(r'^signup$', views.signup, name='signup'),
    url(r'^post_first_job$', views.post_first_job, name='post_first_job'),
    url(r'^login$', auth_views.login, {'template_name': 'business/login.html'}, name='login'),
    url(r'^logout$', auth_views.logout, {'next_page': 'business:index'}, name='logout'),
    url(r'^post_job$', views.post_job, name='post_job'),
    url(r'^offer_results$', views.offer_results, name='offer_results'),
    #url(r'^offers/(?P<offer_id>[0-9]+)/$', views.offer_detail, name='detail'),  # TODO: implement
    url(r'^home$', views.home, name='home'),
    #url(r'^offer_detail/(\?\w[0-9]+)$', views.offer_detail, name='offer_detail'),

    # TODO: Worst hack ever replace for something like: \?id=[0-9]+
    url(r'^offer_detail/.*$', views.offer_detail, name='offer_detail'),
    url(r'^contact_us$', views.contact_us, name='contact_us'),
]
