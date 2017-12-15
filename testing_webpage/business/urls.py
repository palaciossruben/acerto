from django.conf.urls import url
from django.contrib.auth import views as auth_views

from business import views

app_name = 'business'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^post$', views.post_index, name='post_index'),
    url(r'^search$', views.search, name='search'),
    url(r'^results$', views.calculate_result2, name='results'),
    url(r'^signup$', views.signup, name='signup'),
    url(r'^post_first_job$', views.post_first_job, name='post_first_job'),
    url(r'^login$', auth_views.login, {'template_name': 'business/login.html'}, name='login'),
    url(r'^logout$', auth_views.logout, {'next_page': 'business:index'}, name='logout'),
    url(r'^post_job$', views.post_job, name='post_job'),
    url(r'^start$', views.start, name='start'),
    url(r'^start_post$', views.start_post, name='start_post'),
    url(r'^offer_results$', views.offer_results, name='offer_results'),
    url(r'^home$', views.home, name='home'),
    url(r'^dashboard$', views.dashboard, name='dashboard'),

    # TODO: Worst hack ever, replace for something like: \?id=[0-9]+
    url(r'^offer_detail.*$', views.offer_detail, name='offer_detail'),
    url(r'^contact_us$', views.contact_us, name='contact_us'),
    url(r'^results/(?P<pk>\d+)$', views.render_result, name='render_result'),
    url(r'^popup_signup$', views.popup_signup, name='popup_signup'),
    url(r'^plan/(?P<pk>\d+)$', views.plan, name='plan'),
    url(r'^trade_client$', views.trade_client, name='trade_client'),
    url(r'^search_trade$', views.search_trade, name='search_trade'),
]
