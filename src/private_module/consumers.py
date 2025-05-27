import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
import logging
from django.core.cache import cache
from channels.exceptions import DenyConnection

from auth_module.models import User

logger = logging.getLogger("django")


class ChatConsumer(AsyncJsonWebsocketConsumer):
    user: User
    room_group_name: str

    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close(code=403)
            return
        self.room_group_name = f"chat_{self.user.id}"
        await cache.aset(self.room_group_name, "is_online", timeout=60)
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive_json(self, data: dict):
        try:
            message = data["message"]
            if message == "ping":

                await self.channel_layer.group_send(
                    self.room_group_name, {"type": "online_users", "message": {"message":"pong"}}
                )
        except Exception as e:
            logger.warning(e, exc_info=True)

    async def online_users(self, event:dict):
        # get online users that related to that person
        await self.channel_layer.group_send()

    async def chat_message(self, event: dict):
        message = event["message"]
        await self.send_json(message)
