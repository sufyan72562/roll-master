import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import django


# Consumer for Notification
class NotifyConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = 'user_%s' % self.user_id

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def notify_user(self, event):
        print("Received notification event:", event)
        event = json.loads(event["value"])
        username = event.get("username")
        image = event.get("image")
        message = event.get("message")
        try:
            post = event.get("post")
            await self.send(text_data=json.dumps({
                'username': username,
                'image': image,
                'message': message,
                'post': post
            }))
        except Exception as e:
            print("Exception: ", e)
