"""
ASGI config for appproject project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import logging
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from django.conf import settings

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('django.channels')
logger.setLevel(logging.DEBUG)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

# Load Django ASGI application for HTTP handling
django_asgi_app = get_asgi_application()

# Import websocket routing
import codemon.routing

if settings.DEBUG:
    application = ProtocolTypeRouter({
        # HTTP -> Django as usual
        "http": django_asgi_app,
        # WebSocket -> simplified stack for development
        "websocket": URLRouter(
            codemon.routing.websocket_urlpatterns
        ),
    })
else:
    application = ProtocolTypeRouter({
        # HTTP -> Django as usual
        "http": django_asgi_app,
        # WebSocket -> full security stack
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(
                    codemon.routing.websocket_urlpatterns
                )
            )
        ),
    })
