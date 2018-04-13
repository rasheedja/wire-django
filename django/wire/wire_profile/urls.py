from django.urls import path

from . import views
from django.views.generic import TemplateView
from .views import ProfileView, CurrentProfileView, SearchView, SearchMessageView, SearchUserView

app_name = 'wire_profile'
urlpatterns = [
    path('profile/<path:username>', ProfileView.as_view(), name='profile'),
    path('profile/', CurrentProfileView.as_view(), name='current_profile'),
    path('message/<path:username>', views.get_messages, name='get_message'),
    path('messages/<path:user_ids>', views.get_messages_by_ids, name='get_messages_by_ids'),
    path('message/', views.create_message, name='message'),
    path('follow/<path:username>', views.follow_user, name='follow_user'),
    path('followers/<path:username>', views.get_followers, name='get_followers'),
    path('following/<path:username>', views.get_following, name='get_following'),
    path('users/<path:user_ids>', views.get_user_ids, name='get_user_ids'),
    path('user/id/<int:user_id>', views.get_user_id, name='get_user_id'),
    path('search', SearchView.as_view(), name='search'),
    path('search/wire/<path:query>', SearchMessageView.as_view(), name='search_message'),
    path('search/user/<path:query>', SearchUserView.as_view(), name='search_user'),
]
