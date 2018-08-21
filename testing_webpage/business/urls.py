from django.conf.urls import url
from django.contrib.auth import views as auth_views
from business import views

app_name = 'business'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # LOGIN AND LOGOUT
    url(r'^login$', auth_views.login, {'template_name': 'business/login.html', 'extra_context': {'error_message': ''}}, name='login'),
    url(r'^logout$', auth_views.logout, {'next_page': 'business:index'}, name='logout'),
    # CREATE CAMPAIGN
    url(r'^seleccion_gratis$', views.start, name='start'),
    url(r'^seleccion_gratis_enviar$', views.start_post, name='start_post'),
    # CREATE CAMPAIGN WHEN USER IS LOGGED
    url(r'^crear_enviar$', views.create_post, name='create_post'),
    # BUSINESS USER LOGGED
    url(r'^campañas/(?P<business_user_id>\d+)$', views.business_campaigns, name='business_campaigns'),
    url(r'^resumen/(?P<campaign_id>\d+)$', views.summary, name='summary'),
    url(r'^tablero_de_control/(?P<business_user_id>\d+)/(?P<campaign_id>\d+)/(?P<state_name>.*)/$', views.dashboard, name='dashboard'),
    url(r'^perfil_del_candidato/(?P<pk>\d+)$', views.candidate_profile, name='candidate_profile'),
    # CONTACT
    url(r'^contáctanos$', views.contact_form, name='contact_form'),
    url(r'^contact_form_post$', views.contact_form_post, name='contact_form_post'),



    url(r'^search$', views.search, name='search'),
    url(r'^results$', views.calculate_result, name='results'),
    url(r'^signup_choice$', views.signup_choice, name='signup_choice'),
    url(r'^business_signup$', views.business_signup, name='business_signup'),
    url(r'^business_applied$', views.business_applied, name='business_applied'),
    url(r'^home$', views.home, name='home'),
    # TODO: Worst hack ever, replace for something like: \?id=[0-9]+
    url(r'^results/(?P<pk>\d+)$', views.render_result, name='render_result'),
    url(r'^popup_signup$', views.popup_signup, name='popup_signup'),
    url(r'^plan/(?P<pk>\d+)$', views.plan, name='plan'),
]
