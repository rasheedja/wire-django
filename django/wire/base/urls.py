from django.conf.urls import url

from . import views
from django.views.generic import TemplateView

app_name = 'base'
urlpatterns = [
    # ex: /
    url(r'^$', TemplateView.as_view(template_name='base/index.html'), name='home'),
    # ex: /login/
    url(r'^login$', TemplateView.as_view(template_name='base/login.html'), name='login'),
    # ex: /signup/
    url(r'^signup$', TemplateView.as_view(template_name='base/signup.html'), name='signup'),
    url(r'^register$', views.register, name='register'),
    url(r'^verify&', views.verify_user, name='verify'),
    url(r'^logout&', views.log_out, name='logout'),
]
