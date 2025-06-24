from channels.generic.websocket import AsyncJsonWebsocketConsumer
import logging
from django.core.cache import cache
from django_redis import get_redis_connection
from django.conf import settings

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
        await cache.aset(self.room_group_name, "online", timeout=60)
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive_json(self, data: dict, **kwargs):
        try:
            message = data["message"]
            if message == "ping":
                await self.channel_layer.group_send(
                    self.room_group_name, {"type": "online_users", "message": {"message": "pong"}}
                )
        except Exception as e:
            logger.warning(e, exc_info=True)

    async def online_users(self, event: dict):
        online_ttl = settings.ONLINE_TTL
        online_user = await cache.aget(self.room_group_name)
        if online_user is not None:
            await cache.aset(self.room_group_name, online_user, timeout=online_ttl)
        else:
            await cache.aset(self.room_group_name, "online", timeout=online_ttl)
        redis = get_redis_connection("default")

        try:
            cursor = 0
            online_users = []

            while True:
                cursor, keys = await redis.scan(cursor=cursor, match="chat_*", count=100)
                for key in keys:
                    value = await redis.get(key)
                    if value == b"online":
                        user_id = key.decode().replace("chat_", "")
                        online_users.append(user_id)
                if cursor == 0:
                    break

        except Exception as e:
            logger.warning("Error retrieving online users: %s", e, exc_info=True)
            online_users = []

        await self.send_json({"online_users": online_users})

    async def send_message(self, event: dict):
        message = event["message"]
        await self.send_json(message)
