# Create your views here.
from .renderers import UserRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserChangePasswordSerializer, \
    UserDetailSerializer, FollowSerializer
from rollpost.serializers import PostSerializer, ThreadPostSerializer
from rolluser.models import User
from rollpost.models import Posts, ThreadPost
from rest_framework import generics
from .backends import EmailPhoneUsernameAuthenticationBackend as EoP
import json
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
import datetime
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


# Generate Token Manually
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# Create your views here.
class UserRegistrationView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'message': 'Registration Successful', "data": serializer.data}, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('phone')
        password = serializer.data.get('password')
        user = EoP.authenticate(request, username=email, password=password)
        if user is not None:
            token = get_tokens_for_user(user)
            return Response({'token': token, 'User_id': user.id, 'username': user.username, 'image': user.image.url,
                             'msg': 'Login Success'}, status=status.HTTP_200_OK)
        else:
            return Response({'errors': {'non_field_errors': ['Email or Password is not Valid']}},
                            status=status.HTTP_404_NOT_FOUND)


class UserChangePasswordView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserChangePasswordSerializer


class CheckUserView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        data = request.data
        data = data['user']
        user = User.objects.filter(Q(phone=data) | Q(email=data)).first()
        print(user)
        if user:
            return Response({'User_id': user.id, "phone": user.phone}, status=status.HTTP_200_OK)
        else:
            return Response({'msg': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)


class UserDetailUpdateView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        detail = User.objects.get(id=pk)
        serializer = UserDetailSerializer(detail)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        detail = User.objects.get(id=pk)
        serializer = UserDetailSerializer(detail, request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# user profile
class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None, username=None):
        followed = False
        post_dict = dict()
        following_usernames = request.user.followers.values_list('username', flat=True)

        if username in following_usernames:
            followed = True

        user = User.objects.get(username=username)
        if Posts.objects.filter(user=user):
            pagination_class = PageNumberPagination
            pagination_class.page_size = 10
            paginator = pagination_class()
            post = Posts.objects.filter(user=user).order_by("-pk")
            page = paginator.paginate_queryset(post, request)
            for pos in page:
                if pos.is_thread == 0:
                    serial = PostSerializer(pos, context={'request': request})
                    post_dict[pos.id] = serial.data
                if pos.is_thread == 1:
                    post_list = list()
                    serializ = PostSerializer(pos, context={'request': request})
                    post_list.append(serializ.data)
                    threadpost = ThreadPost.objects.filter(post_id=pos.id)
                    for pst in threadpost:
                        pstserialize = ThreadPostSerializer(pst)
                        post_list.append(pstserialize.data)
                    post_dict[pos.id] = post_list
        post_id: list = list()
        for i in post_dict:
            post_id.append(i)
        detail = User.objects.get(username=username)
        serializer = UserDetailSerializer(detail)
        return Response({
            "profile": serializer.data,
            "followed": followed,
            "ids": post_id,
            "post": post_dict
        },
            status=status.HTTP_200_OK
        )


class FollowUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None, username=None):
        to_user = User.objects.get(username=username)
        print(to_user.id)
        from_user = self.request.user
        follow = None
        if from_user.is_authenticated:
            if from_user != to_user:
                if from_user in to_user.followers.all():
                    follow = False
                    from_user.following.remove(to_user)
                    to_user.followers.remove(from_user)
                else:
                    follow = True
                    from_user.following.add(to_user)
                    to_user.followers.add(from_user)
                    payload = {}
                    payload["username"] = self.request.user.username
                    payload["image"] = self.request.user.image.url
                    payload["message"] = "Follows You"
                    # sending notifications
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        'user_%s' % to_user.id, {
                            'type': 'notify_user',
                            'value': json.dumps(payload)
                        }
                    )
        data = {
            'follow': follow
        }
        return Response(data)


class GetFollowersView(generics.ListAPIView):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        username = self.kwargs['username']
        queryset = User.objects.get(
            username=username).followers.all()
        return queryset


class GetFollowingView(generics.ListAPIView):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        username = self.kwargs['username']
        queryset = User.objects.get(
            username=username).following.all()
        return queryset


class RefereshPost(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None, username=None):
        post_dict = dict()
        following_ids = request.user.following.values_list('id', flat=True)
        posts_list = Posts.objects.filter(Q(user__in=following_ids) | Q(user=request.user)).order_by("-pk")
        pagination_class = PageNumberPagination
        pagination_class.page_size = 10
        paginator = pagination_class()
        page = paginator.paginate_queryset(posts_list, request)
        for pos in page:
            if pos.is_thread == 0:
                serial = PostSerializer(pos, context={'request': request})
                post_dict[pos.id] = serial.data
            if pos.is_thread == 1:
                post_list = list()
                serializ = PostSerializer(pos, context={'request': request})
                post_list.append(serializ.data)
                threadpost = ThreadPost.objects.filter(post_id=pos.id)
                for pst in threadpost:
                    pstserialize = ThreadPostSerializer(pst)
                    post_list.append(pstserialize.data)
                post_dict[pos.id] = post_list
        post_id: list = list()
        for i in post_dict:
            post_id.append(i)
        return Response({"ids": post_id, "data": post_dict}, status=status.HTTP_200_OK)


class RandomPost(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None, username=None):
        post_dict = dict()
        following_ids = request.user.following.values_list('id', flat=True)
        posts_list = Posts.objects.all().exclude(user__in=following_ids).order_by("-pk")
        pagination_class = PageNumberPagination
        pagination_class.page_size = 10
        paginator = pagination_class()
        page = paginator.paginate_queryset(posts_list, request)
        for pos in page:
            if pos.is_thread == 0:
                serial = PostSerializer(pos, context={'request': request})
                post_dict[pos.id] = serial.data
            if pos.is_thread == 1:
                post_list = list()
                serializ = PostSerializer(pos, context={'request': request})
                post_list.append(serializ.data)
                threadpost = ThreadPost.objects.filter(post_id=pos.id)
                for pst in threadpost:
                    pstserialize = ThreadPostSerializer(pst)
                    post_list.append(pstserialize.data)
                post_dict[pos.id] = post_list

        post_id: list = list()
        for i in post_dict:
            post_id.append(i)
        return Response({"ids": post_id, "data": post_dict}, status=status.HTTP_200_OK)


class HomeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None, username=None):
        post_dict = dict()
        story_dict = dict()
        following_ids = request.user.following.values_list('id', flat=True)
        posts_list = Posts.objects.filter(Q(user__in=following_ids) | Q(user=request.user)).order_by("-pk")
        storys_list = Posts.objects.filter(
            Q(user__in=following_ids, timestamp__gte=datetime.date.today()) | Q(user=request.user,
                                                                                timestamp__gte=datetime.date.today())).order_by(
            "-pk")
        pagination_class = PageNumberPagination
        pagination_class.page_size = 10
        paginator = pagination_class()
        page = paginator.paginate_queryset(posts_list, request)
        page1 = paginator.paginate_queryset(storys_list, request)
        # for stories
        for poss in page1:
            if poss.is_thread == 0:
                serializ = PostSerializer(poss, context={'request': request})
                story_dict[poss.id] = serializ.data
            if poss.is_thread == 1:
                story_list = list()
                serializz = PostSerializer(poss, context={'request': request})
                story_list.append(serializz.data)
                threadposts = ThreadPost.objects.filter(post_id=poss.id)
                for pstt in threadposts:
                    psttserialize = ThreadPostSerializer(pstt)
                    story_list.append(psttserialize.data)
                story_dict[poss.id] = story_list
        # for followed person post
        for pos in page:
            if pos.is_thread == 0:
                serial = PostSerializer(pos, context={'request': request})
                post_dict[pos.id] = serial.data
            if pos.is_thread == 1:
                post_list = list()
                serializ = PostSerializer(pos, context={'request': request})
                post_list.append(serializ.data)
                threadpost = ThreadPost.objects.filter(post_id=pos.id)
                for pst in threadpost:
                    pstserialize = ThreadPostSerializer(pst)
                    post_list.append(pstserialize.data)
                post_dict[pos.id] = post_list
        post_id: list = list()
        story_id: list = list()
        for j in post_dict:
            post_id.append(j)
        for z in story_dict:
            story_id.append(z)

        return Response({
            "post_id": post_id,
            "story_id": story_id,
            "stories": story_dict,
            "post": post_dict
        },
            status=status.HTTP_200_OK
        )


# searching users
class SearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None, username=None):
        users = User.objects.filter(username__istartswith=username)
        userserializer = FollowSerializer(users, many=True)

        return Response(userserializer.data, status=status.HTTP_200_OK)


class DeleteUserVIew(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None, id=None):
        user = User.objects.get(pk=id)
        user.delete()
        return Response(
            {
                "success": " User Successfully Deleted"
            }
        )
