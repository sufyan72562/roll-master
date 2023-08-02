from rest_framework import serializers
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'sender', 'text', 'timestamp', 'is_seen', 'image']

    def get_sender(self, obj):
        return {
            "sender_name": obj.sender.firstname + " " + obj.sender.lastname,
            "sender_image": obj.sender.image.url,
            "sender_id": obj.sender.id
        }


class ConversationSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    other_participant = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'last_message', 'other_participant']

    def get_last_message(self, obj):
        last_message = obj.messages.last()  # Directly access the last message from the prefetched data
        if last_message:
            serializer = MessageSerializer(last_message)
            return serializer.data
        else:
            return None

    def get_other_participant(self, obj):
        request_user = self.context['request'].user
        participants = obj.participants.all()
        for participant in participants:
            if participant != request_user:
                return {
                    "participant_name": participant.firstname + " " + participant.lastname,
                    "participant_image": participant.image.url,
                    "participant_id": participant.id
                }
        return None



