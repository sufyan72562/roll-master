from django.urls import path

from rollchat.views import ConversationListAPIView, MessagesView, DeleteMessageView
urlpatterns = [
    path('conversations/', ConversationListAPIView.as_view(), name='conversation-list'),
    path('messages/<str:conversation_id>', MessagesView.as_view(), name='message-list'),
    path('delete_message/<int:id>', DeleteMessageView.as_view(), name='delete-message'),

]
