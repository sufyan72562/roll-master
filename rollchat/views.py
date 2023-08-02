import json

from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination

"""
Things need to be fixed:
Response of stories and posts must contain thumbnail of video.
Posts or story must contain number of comments and likes.
The comment must contain user info required by design (name, image, id).
The post must contain the flag if I liked or not.
Search is not providing correct results.

Things need to be developed/added:
The whole chat system.
Chat must be via web sockets.
Notifications endpoint not implemented.

And deployment of application to the server
"""

from .models import Conversation, Message
from rolluser.models import User
from .serializers import ConversationSerializer, MessageSerializer
from django.db.models import Count
from django.db.models import Prefetch


class ConversationListAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

    def create(self, request, *args, **kwargs):
        try:
            participants = request.data.get('participants', [])
            if len(participants) <= 1:
                response = {"message": "Invalid participant(s)", "status": "false"}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            existing_conversation = self.get_existing_conversation(participants)

            if existing_conversation:
                serializer = self.get_serializer(existing_conversation)
                return Response(serializer.data, status=status.HTTP_200_OK)

            if self.are_participants_valid(participants):
                conversation = Conversation.objects.create()
                conversation.participants.set(participants)

                serializer = self.get_serializer(conversation)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                response = {"message": "Invalid participant(s)", "status": "false"}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            response = {"message": "Couldn't create conversation", "status": "false"}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def get_existing_conversation(self, participants):
        existing_conversations = Conversation.objects.annotate(participant_count=Count('participants')).filter(
            participant_count=len(participants))
        for conversation in existing_conversations:
            if list(conversation.participants.values_list('id', flat=True)) == participants:
                return conversation
        return None

    def are_participants_valid(self, participants):
        # Check if all participants exist in the database
        user_ids = [participant for participant in participants if User.objects.filter(pk=participant).exists()]
        return len(user_ids) == len(participants)


    def get_queryset(self):
        # Prefetch the related messages and sender objects to optimize queries
        current_user = self.request.user
        queryset = Conversation.objects.prefetch_related(
            Prefetch('messages', queryset=Message.objects.order_by('-timestamp'))
        ).filter(participants__in=[current_user])
        return queryset

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            response = {"message": "Not found", "status": "false"}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class MessagesView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        try:
            conversation_id = self.kwargs['conversation_id']
            Message.objects.filter(conversation=int(conversation_id)).update(is_seen=True)

            queryset = Message.objects.filter(conversation=int(conversation_id)).order_by('-timestamp')
            page_size = self.request.GET.get('page_size', 10)  # Default page size is 10
            self.pagination_class.page_size = page_size
            paginated_queryset = self.paginate_queryset(queryset)

            return paginated_queryset
        except Exception as e:
            error_message = "No messages found"
            # You can log the exception if needed: logger.exception(e)
            return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)


class DeleteMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None, id=None):
        try:
            chat = Message.objects.get(pk=int(id))
            chat.delete()
            return Response(
                {
                    "success": "Message Deleted Successfully!"
                }
            )
        except Exception as e:
            response = {
                "message": "Message not deleted"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
