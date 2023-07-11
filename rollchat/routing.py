import django
django.setup()
from rollchat.consumers import ChatConsumer, NotifyConsumer
from django.conf.urls import url

websocket_urlpatterns = [
    url(r'ws/chat/(?P<room_name>\w+)/$', ChatConsumer.as_asgi()),
    url(r'^ws/notify/(?P<room_name>[^/]+)/$', NotifyConsumer.as_asgi()),
]
