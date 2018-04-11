from django.urls import path

from . import views
from django.views.generic import TemplateView
from .views import ProfileView

app_name = 'wire_profile'
urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('message/<path:username>', views.get_messages, name='get_message'),
    path('message/', views.create_message, name='message')
]
