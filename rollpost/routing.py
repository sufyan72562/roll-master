from django.urls import re_path
from rollpost.consumers import NotifyConsumer

websocket_urlpatterns = [
    re_path(r'^ws/notification/(?P<user_id>[^/]+)/$', NotifyConsumer.as_asgi()),
]
