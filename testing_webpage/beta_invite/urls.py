from django.conf.urls import url

from . import views

app_name = 'beta_invite'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^registro$', views.register, name='register'),
    url(r'^pruebas$', views.tests, name='tests'),
    url(r'^test_result$', views.get_test_result, name='test_result'),
    url(r'^interview/(?P<pk>\d+)$', views.interview, name='interview'),
    url(r'^add_cv$', views.add_cv),
    url(r'^add_cv_changes$', views.add_cv_changes),
]
