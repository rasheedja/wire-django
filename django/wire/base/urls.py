from django.urls import path

from . import views
from django.views.generic import TemplateView

app_name = 'base'
urlpatterns = [
    path('', TemplateView.as_view(template_name='base/index.html'), name='home'),
    path('login', TemplateView.as_view(template_name='base/login.html'), name='login'),
    path('signup', TemplateView.as_view(template_name='base/signup.html'), name='signup'),
    path('register', views.register, name='register'),
    path('verify', views.verify_user, name='verify'),
    path('logout', views.log_out, name='logout'),
    path('get-recommended-users/<path:excluded_username>', views.recommended_users, name='recommended_users')
]
