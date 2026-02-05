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

# Import websocket routing and custom auth middleware
import codemon.routing
from codemon.auth_middleware import AccountAuthMiddlewareStack

# Channels ProtocolTypeRouter設定
# WebSocket接続をChannels経由で処理し、その他はDjangoで処理
application = ProtocolTypeRouter({
    # HTTP -> Django通常処理
    "http": django_asgi_app,
    # WebSocket -> Channels処理（カスタム認証ミドルウェア使用）
    "websocket": AccountAuthMiddlewareStack(
        URLRouter(
            codemon.routing.websocket_urlpatterns
        )
    ),
})

