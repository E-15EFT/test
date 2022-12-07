from django.urls import path
from .views import *
from django.views.generic.base import RedirectView

urlpatterns = [
    path('create_friend/', create_friend, name='create_friend'),
    path('friend-list/', friend_list, name='friend-list'),
    path('chat/<str:room_name>/', start_chat, name='start_chat'),
]
