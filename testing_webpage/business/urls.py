from django.conf.urls import url
from django.contrib.auth import views as auth_views
from business import views

app_name = 'business'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # LOGIN AND LOGOUT
    url(r'^login$', auth_views.login, {'template_name': 'business/login.html', 'extra_context': {'error_message': ''}},
        name='login'),
    url(r'^logout$', auth_views.logout, {'next_page': 'business:index'}, name='logout'),
    # CREATE CAMPAIGN
    url(r'^seleccion[-_]gratis$', views.start, name='start'),
    url(r'^seleccion[-_]gratis[-_]enviar$', views.start_post, name='start_post'),
    # CREATE CAMPAIGN WHEN USER IS LOGGED
    url(r'^crear[-_]enviar$', views.create_post, name='create_post'),
    # BUSINESS USER LOGGED
    url(r'^campañas/(?P<business_user_id>\d+)$', views.business_campaigns, name='business_campaigns'),
    url(r'^resumen/(?P<campaign_id>\d+)$', views.summary, name='summary'),
    url(r'^online[-_]demo$', views.online_demo, name='online_demo'),
    url(r'^tablero[-_]de[-_]control/(?P<business_user_id>\d+)/(?P<campaign_id>\d+)/(?P<state_name>.*)/$', views.dashboard, name='dashboard'),
    url(r'^perfil[-_]del[-_]candidato/(?P<candidate_id>\d+)$', views.candidate_profile, name='candidate_profile'),
    # CONTACT
    url(r'^contactanos$', views.contact_form, name='contact_form'),
    url(r'^contact[-_]form[-_]post$', views.contact_form_post, name='contact_form_post'),
    # START
    url(r'^get[-_]work[-_]area[-_]requirement/(?P<work_area_id>\d+)$', views.get_work_area_requirement, name='get_work_area_requirement'),
    # PAYU
    url(r'payment[-_]confirmation$', views.payment_confirmation, name='payment_confirmation'),
    # DEMO SCHEDULED
    url(r'^demo[-_]scheduled$', views.demo_scheduled, name='demo_scheduled'),
    # SAVE CANDIDATE COMMENTS
    url(r'^save[-_]comments$', views.save_comments, name='save_comments'),
    # CHANGE CANDIDATE STATE
    url(r'^change[-_]state$', views.change_state, name='change_state'),

    # TODO: This search url should be deleted?
    url(r'^search$', views.search, name='search'),
    url(r'^results$', views.calculate_result, name='results'),
    url(r'^business[-_]signup$', views.business_signup, name='business_signup'),
    url(r'^home$', views.home, name='home'),
    # TODO: Worst hack ever, replace for something like: \?id=[0-9]+
    url(r'^results/(?P<pk>\d+)$', views.render_result, name='render_result'),
]

'''
url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    auth_views.password_reset_confirm, name='password_reset_confirm'),
url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
'''