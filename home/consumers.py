import json
from channels.generic.websocket import AsyncWebsocketConsumer

class EmergencyAlertConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("emergency_alerts", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("emergency_alerts", self.channel_name)

    async def send_alert(self, event):
        alert_data = event['alert']
        await self.send(text_data=json.dumps(alert_data))
