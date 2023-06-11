
from rest_framework.views import APIView
from rollpost.serializers import PostSerializer, AuthorSerializer, ThreadPostSerializer, CommentSerializer, \
    CommentReplySerializer, ReportAdminSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rollpost.models import Posts, ThreadPost, Comment, CommentReply, ReportAdmin
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import  MultiPartParser, FormParser
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json
import base64
import uuid


# Create your views here.
class Upload(APIView):
    permission_classes = [IsAuthenticated]
    parser_classess = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        data = request.data.get("image")
        if not data == "":
            predata: list = list()
            predata = data
            newdata: list = list()
            for i in predata:
                temp = base64.b64decode((i["image"]))
                filename = f'./media/post/images/{uuid.uuid4()}.png'
                with open(filename, 'wb') as f:
                    f.write(temp)
                i['image'] = filename
                newdata.append(i)
            serializer = PostSerializer(data=newdata, many=True, context={'request': request})
        else:
            serializer = PostSerializer(data=data, many=True, context={'request': request})
        if serializer.is_valid():
            # serializer.validated_data['user'] = request.user
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors)


class Uploadthread(APIView):
    permission_classes = [IsAuthenticated]
    parser_classess = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        post = Posts.objects.create(user=request.user, is_thread=1, caption=request.data['post'][0]['caption'])
        post.save()
        temp = request.data['post']
        temp.pop(0)
        data = temp
        print(data)
        if not data[1]["image"] == "":
            predata: list = list()
            predata = data
            newdata: list = list()
            for i in predata:
                temp = base64.b64decode((i["image"]))
                filename = f'./media/post/images/{uuid.uuid4()}.png'
                with open(filename, 'wb') as f:
                    f.write(temp)
                i['image'] = filename
                newdata.append(i)
            serializer = ThreadPostSerializer(data=newdata, many=True)
        else:
            serializer = ThreadPostSerializer(data=data, many=True)
        if serializer.is_valid():
            for i in range(0, len(serializer.validated_data)):
                serializer.validated_data[i]['post_id'] = post
            serializer.save()
            return Response({"success": serializer.data})

        return Response(serializer.errors)


# Views Update of posts
class UpdateViews(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None, id=None):
        post = Posts.objects.filter(pk=id).first()
        post.views += 1
        post.save()

        return Response({"success": "View Added"})


class LikeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None, id=None):
        try:
            post = Posts.objects.get(pk=id)
            postowner = post.user.id
            user = self.request.user
            like = bool()
            if user.is_authenticated:
                if user in post.likes.all():
                    like = False
                    post.likes.remove(user)
                else:
                    like = True
                    post.likes.add(user)
                    payload = {}
                    payload["username"] = self.request.user.username
                    payload["image"] = self.request.user.image.url
                    payload["message"] = "Likes Your Post"
                    payload["post"] = id
                    # sending notifications
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        'user_%s' % postowner, {
                            'type': 'notify_user',
                            'value': json.dumps(payload)
                        }
                    )
            data = {
                'like': like
            }
            return Response(data)
        except Exception as e:
            print(e)
            return Response(data={})


class GetLikersView(generics.ListAPIView):
    serializer_class = AuthorSerializer

    def get_queryset(self):
        post_id = self.kwargs['id']
        queryset = Posts.objects.get(
            pk=post_id).likes.all()
        return queryset


# comment Upload
class UploadComment(APIView):
    permission_classes = [IsAuthenticated]
    parser_classess = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            payload = {}
            payload["username"] = self.request.user.username
            payload["image"] = self.request.user.image.url
            payload["message"] = "Comment on your post"
            payload["post"] = serializer.validated_data['posts'].id
            post = Posts.objects.filter(pk=int(payload['post'])).first()
            postowner = post.user.id
            if postowner != request.user.id:
                # sending notiifications
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    'user_%s' % postowner, {
                        'type': 'notify_user',
                        'value': json.dumps(payload)
                    }
                )
            return Response(serializer.data)

        return Response(serializer.errors)


# comment reply upload
class ReplyComment(APIView):
    permission_classes = [IsAuthenticated]
    parser_classess = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        serializer = CommentReplySerializer(data=request.data)
        if serializer.is_valid():
            parentpost = serializer.validated_data['parent']
            comment = Comment.objects.get(id=parentpost.id)
            comment.is_reply = 1
            comment.save()
            serializer.save()
            payload = {}
            payload["username"] = self.request.user.username
            payload["image"] = self.request.user.image.url
            payload["message"] = "Comment on your post"
            commnt = serializer.validated_data['parent']
            commentt = Comment.objects.filter(pk=commnt.id).first()
            payload["post"] = commentt.posts.id
            postt = Posts.objects.filter(pk=commentt.posts.id).first()
            print(postt)
            postowner = postt.user.id
            if postowner != request.user.id:
                # sending notiifications
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    'user_%s' % postowner, {
                        'type': 'notify_user',
                        'value': json.dumps(payload)
                    }
                )
            return Response(serializer.data)
        return Response(serializer.errors)


# get posts all comments
class CommentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        postserialize = None
        post_dict = dict()
        if Comment.objects.filter(posts=id):
            pagination_class = PageNumberPagination
            pagination_class.page_size = 2
            paginator = pagination_class()
            post = Comment.objects.filter(posts=id).order_by("-pk")
            page = paginator.paginate_queryset(post, request)
            for pos in page:
                if pos.is_reply == 0:
                    serial = CommentSerializer(pos)
                    post_dict[pos.id] = serial.data
                if pos.is_reply == 1:
                    post_list = list()
                    serial = CommentSerializer(pos)
                    post_list.append(serial.data)
                    replycomment = CommentReply.objects.filter(parent=pos.id)
                    for pst in replycomment:
                        pstserialize = CommentReplySerializer(pst)
                        post_list.append(pstserialize.data)
                    post_dict[pos.id] = post_list
        return Response({
            "comment": post_dict
        })


class GetPostView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None, id=None):
        post_dict = dict()
        post = Posts.objects.all().filter(pk=id).first()
        print(post)
        if post.is_thread == 0:
            serial = PostSerializer(post, context={'request': request})
            post_dict[post.id] = serial.data
        if post.is_thread == 1:
            post_list = list()
            serializ = PostSerializer(post, context={'request': request})
            post_list.append(serializ.data)
            threadpost = ThreadPost.objects.filter(post_id=post.id)
            for pst in threadpost:
                pstserialize = ThreadPostSerializer(pst)
                post_list.append(pstserialize.data)
            post_dict[post.id] = post_list

        return Response(post_dict)


class DeletePostVIew(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None, id=None):
        post = Posts.objects.get(pk=id)
        post.delete()
        return Response(
            {
                "success": " Post Successfully Deleted"
            }
        )


class DeleteCommentVIew(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None, id=None):
        comment = Comment.objects.get(pk=id)
        comment.delete()
        return Response(
            {
                "success": "Comment Successfully Deleted"
            }
        )


class DeleteReplyCommentVIew(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None, id=None):
        comment = CommentReply.objects.get(pk=id)
        comment.delete()
        return Response(
            {
                "success": "Comment Successfully Deleted"
            }
        )


class ReportAdminView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = ReportAdminSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['user'] = request.user
            serializer.save()
            return Response({"data": serializer.data})
        else:
            return Response(serializer.errors)


class AllReportAdminView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        data = ReportAdmin.objects.all()
        print(data)
        pagination_class = PageNumberPagination
        pagination_class.page_size = 2
        paginator = pagination_class()
        page = paginator.paginate_queryset(data, request)
        print(page)
        serializer = ReportAdminSerializer(page, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetComment(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None, id=None):
        data = Comment.objects.filter(pk=id)
        print(data)
        serializer = CommentSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetReplyComment(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None, id=None):
        data = CommentReply.objects.all().filter(pk=id)
        serializer = CommentReplySerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
