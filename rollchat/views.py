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
from .serializers import ConversationSerializer, MessageSerializer


class ConversationListAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

    def create(self, request, *args, **kwargs):
        try:
            # Create a new conversation and add participants
            participants = request.data.get('participants', [])
            conversation = Conversation.objects.create()
            conversation.participants.set(participants)

            serializer = self.get_serializer(conversation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            response = {"message": "Couldn't created", "status": "false"}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
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
