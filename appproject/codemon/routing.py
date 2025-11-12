from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # Example: ws://<host>/ws/chat/1/
    re_path(r'^ws/chat/(?P<thread_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
]
