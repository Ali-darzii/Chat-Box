import json

from channels.generic.websocket import AsyncWebsocketConsumer
import logging

from auth_module.models import User

logger = logging.getLogger("django")


class ChatConsumer(AsyncWebsocketConsumer):
    room_group_name = None

    async def connect(self):
        user_id = self.scope["user"].id
        self.room_group_name = f"chat_{user_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        try:
            _ = text_data["message"]
            logger.critical(text_data)
            await self.channel_layer.group_send(
                self.room_group_name, {"message": "pong"}
            )
        except Exception as e:
            logger.warning(e, exc_info=True)

    # Receive message from room group
    async def chat_message(self, event: dict):
        message = event["message"]

        await self.send(text_data=json.dumps({"message": message}))
