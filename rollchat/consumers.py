from channels.generic.websocket import AsyncWebsocketConsumer
import json
from rollchat.serializers import MessageSerializer

from rollchat.models import Message, Conversation
from channels.db import database_sync_to_async

from rolluser.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Handle received message
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_id = text_data_json['sender_id']
        image = text_data_json.get('image')
        sender = await database_sync_to_async(User.objects.get)(pk=int(sender_id))

        # Save message to the database
        conversation = await database_sync_to_async(Conversation.objects.get)(pk=int(self.room_name))
        if image:
            message_obj = await database_sync_to_async(Message.objects.create)(conversation=conversation,
                                                                               sender=sender,
                                                                               text=message,
                                                                               image=image)
        else:
            message_obj = await database_sync_to_async(Message.objects.create)(conversation=conversation,
                                                                               sender=sender,
                                                                               text=message)

        # Send message to the WebSocket group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'sender_info': MessageSerializer(message_obj).data,
                # 'message': message,
                # 'image': image if image else None,
            }
        )

    async def send_message(self, event):
        # Send message to WebSocket
        sender = event['sender']
        message = event['message']

        # Send the message to the WebSocket
        await self.send(text_data=json.dumps({
            'sender': sender,
            'message': message
        }))

    async def chat_message(self, event):
        # Send message to WebSocket group
        await self.send(text_data=json.dumps(event))


class NotifyConsumer(AsyncWebsocketConsumer):

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
        post = None
        sender_id = text_data_json.get('sender_id')
        image = text_data_json.get('image')
        message = text_data_json.get('message')
        message_id = text_data_json.get('message_id')

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'notify_user',
                'sender_id': sender_id,
                'image': image,
                'message': message,
                'message_id': message_id,
            })

    async def notify_user(self, event):
        print(event)

        sender_id = event.get("sender_id")
        message = event.get("message")
        image = event.get("image")
        message_id = event.get("message_id")
        sender = await database_sync_to_async(User.objects.get)(pk=int(sender_id))
        await self.send(text_data=json.dumps({
            'user_fullname': sender.firstname + " " + sender.lastname,
            'user_image': sender.image.url,
            'message': message,
            'image': image,
            'message_id': message_id,
        }))
