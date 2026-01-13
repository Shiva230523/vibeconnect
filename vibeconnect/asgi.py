"""
ASGI config for vibeconnect project.

Supports both:
✅ HTTP requests (Django views)
✅ WebSocket connections (Django Channels)
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

import chat.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vibeconnect.settings")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(
            URLRouter(chat.routing.websocket_urlpatterns)
        ),
    }
)
