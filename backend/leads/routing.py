from django.urls import path

from leads.consumers import LeadUpdatesConsumer

websocket_urlpatterns = [
    path("ws/leads/", LeadUpdatesConsumer.as_asgi()),
]

