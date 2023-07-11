from rest_framework import serializers
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'sender', 'text', 'timestamp', 'is_seen']

    def get_sender(self, obj):
        return {
            "sender_name": obj.sender.firstname + " " + obj.sender.lastname,
            "sender_image": obj.sender.image.url
        }


class ConversationSerializer(serializers.ModelSerializer):
    # messages = MessageSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'last_message']

    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-timestamp').first()
        if last_message:
            serializer = MessageSerializer(last_message)
            return serializer.data
        else:
            return None
