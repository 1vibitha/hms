from django.urls import re_path
from .consumers import EmergencyAlertConsumer

websocket_urlpatterns = [
    re_path(r'ws/emergency-alerts/$', EmergencyAlertConsumer.as_asgi()),
]
