import os
from dotenv import load_dotenv

load_dotenv()

env = os.environ.get('ENV', 'local')
settings_map = {
    'local': 'backend.settings.local',
    'development': 'backend.settings.development',
    'stage': 'backend.settings.stage',
    'production': 'backend.settings.production',
}
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_map.get(env, 'backend.settings.local'))

from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import api.Websocket.routings

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(api.Websocket.routings.websocket_urlpatterns)
    ),
})
