from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rolluser.renderers import UserRenderer
from .models import Chat, ChatRoom
from .serializers import ChatSerializer


# Create your views here.
class UserChatRoom(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        room = ChatRoom.objects.filter(name=id).first()
        if room:
            chats = Chat.objects.filter(room=room)[::-1]
            serializer = ChatSerializer(chats, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            room = ChatRoom(name=id)
            room.save()
            return Response({"success": "Room Created"})


class DeleteMessageVIew(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None, id=None):
        chat = Chat.objects.get(pk=id)
        chat.delete()
        return Response(
            {
                "success": "Message Successfully Deleted"
            }
        )
