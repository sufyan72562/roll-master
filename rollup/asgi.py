import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import rollchat.routing
import rollpost.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rollup.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(URLRouter(rollpost.routing.websocket_urlpatterns
                                               + rollchat.routing.websocket_urlpatterns)),

})
