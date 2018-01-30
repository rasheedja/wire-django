from django.conf.urls import url

from . import views
from django.views.generic import TemplateView
from .views import ProfileView

app_name = 'wire_profile'
urlpatterns = [
    # ex: /profile
    url('profile/', ProfileView.as_view(), name='profile'),
    url('message/', views.create_message, name='message')
]
