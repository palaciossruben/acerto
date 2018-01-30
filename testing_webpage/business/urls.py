from django.conf.urls import url
from django.contrib.auth import views as auth_views

from business import views

app_name = 'business'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search$', views.search, name='search'),
    url(r'^results$', views.calculate_result2, name='results'),
    url(r'^login$', auth_views.login, {'template_name': 'business/login.html'}, name='login'),
    url(r'^logout$', auth_views.logout, {'next_page': 'business:index'}, name='logout'),
    url(r'^start$', views.start, name='start'),
    url(r'^signup_choice$', views.signup_choice, name='signup_choice'),
    url(r'^business_signup$', views.business_signup, name='business_signup'),
    url(r'^business_applied$', views.business_applied, name='business_applied'),
    url(r'^start_post$', views.start_post, name='start_post'),
    url(r'^home$', views.home, name='home'),
    url(r'^dashboard/(?P<pk>\d+)$', views.dashboard, name='dashboard'),
    url(r'^candidate_profile/(?P<pk>\d+)$', views.candidate_profile, name='candidate_profile'),

    # TODO: Worst hack ever, replace for something like: \?id=[0-9]+
    url(r'^contact_us$', views.contact_us, name='contact_us'),
    url(r'^results/(?P<pk>\d+)$', views.render_result, name='render_result'),
    url(r'^popup_signup$', views.popup_signup, name='popup_signup'),
    url(r'^plan/(?P<pk>\d+)$', views.plan, name='plan'),
    url(r'^trade_client$', views.trade_client, name='trade_client'),
    url(r'^search_trade$', views.search_trade, name='search_trade'),

    url(r'^send_reset_url', views.send_reset_url, name='send_reset_url'),
    url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
]
