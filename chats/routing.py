from django.urls import path, include

from . import consumers

websocket_urlpatterns = [
    path('ws/client/', consumers.ClientConsumer.as_asgi()),
]
