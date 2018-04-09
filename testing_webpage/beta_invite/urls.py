from django.conf.urls import url

from . import views

app_name = 'beta_invite'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^registro$', views.register, name='register'),
    url(r'^pruebas$', views.tests, name='tests'),
    url(r'^test_result$', views.get_test_result, name='test_result'),
    url(r'^add_cv$', views.add_cv, name='add_cv'),
    url(r'^add_cv_changes$', views.add_cv_changes),
    url(r'^additional_info$', views.additional_info, name='additional_info'),
    url(r'^save_partial_additional_info$', views.save_partial_additional_info, name='save_partial_additional_info'),
    url(r'^active_campaigns', views.active_campaigns, name='active_campaigns'),
]
