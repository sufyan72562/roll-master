from django.urls import path
from .views import UserChatRoom,DeleteMessageVIew

urlpatterns = [
    path('userchat/<str:id>', UserChatRoom.as_view(), name='userchat'),
    path('delete-message/<int:id>', DeleteMessageVIew.as_view(), name='deletemessage'),
]