import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import django

django.setup()
from rollchat.models import Chat, ChatRoom
from rolluser.models import User


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        imagebase = str()
        try:
            imagebase = text_data_json['imagebase']
            # img = Image.open(BytesIO(base64.b64decode(imagebase)))
        except:
            pass

        message = text_data_json['message']
        # self.user_id = self.scope['user'].id
        self.user_id = text_data_json['user_id']
        # Find room object
        room = await database_sync_to_async(ChatRoom.objects.get)(name=self.room_name)
        userid = await database_sync_to_async(User.objects.get)(id=self.user_id)
        print(len(imagebase))
        # Create new chat object
        if imagebase:
            chat = Chat(
                content=message,
                imaage=imagebase,
                user=userid,
                # user=self.scope['user'],
                room=room
            )
        else:
            chat = Chat(
                content=message,
                user=userid,
                # user=self.scope['user'],
                room=room
            )

        await database_sync_to_async(chat.save)()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message_id': chat.id,
                'message': message,
                'imagebase': imagebase,
                'user_id': self.user_id
            })

    async def chat_message(self, event):
        message = event['message']
        user_id = event['user_id']
        imagebase = ['imagebase']
        message_id = event['message_id']

        await self.send(text_data=json.dumps({
            'message': message,
            'user_id': user_id,
            'imagebase': imagebase,
            'message_id': message_id

        }))


# Consumer for Notification
class NotifyConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'user_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        post = None
        username = text_data_json['username']
        image = text_data_json['image']
        message = text_data_json['message']
        try:
            post = text_data_json['post']
        except:
            pass

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'notify_user',
                'username': username,
                'image': image,
                'message': message,
                'post': post
            })

    async def notify_user(self, event):
        print(event)
        event = json.loads(event['value'])
        username = event["username"]
        image = event["image"]
        message = event["message"]
        try:
            post = None
            post = event["post"]
        except:
            pass

        await self.send(text_data=json.dumps({
            'username': username,
            'image': image,
            'message': message,
            'post': post
        }))
