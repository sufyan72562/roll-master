from rest_framework import serializers
from rollpost.models import Posts, ThreadPost, Comment, CommentReply, ReportAdmin
from rolluser.models import User
import base64
from django.conf import settings
import os
from moviepy.editor import VideoFileClip


class PostSerializer(serializers.ModelSerializer):
    number_of_comments = serializers.SerializerMethodField()
    number_of_likes = serializers.SerializerMethodField()
    liked_by_current_user = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Posts
        fields = '__all__'

    def get_username(self, obj):
        return obj.user.username

    def get_image(self, obj):
        return obj.user.image.url

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['username'] = self.get_username(instance)
        data['userimage'] = self.get_image(instance)
        return data

    def get_number_of_comments(self, obj):
        comments_list = Comment.objects.filter(posts=obj).values_list("id", flat=True)
        comments_replies_count = CommentReply.objects.filter(parent__in=comments_list).count()
        return len(comments_list) + comments_replies_count

    def get_number_of_likes(self, obj):
        return obj.likes.count()

    def get_liked_by_current_user(self, obj):
        # Access the request object from the serializer's context
        try:
            request = self.context.get('request')
            # Check if the request has an authenticated user
            if request.user.is_authenticated and obj.likes.filter(id=request.user.id).exists():
                return True
        except Exception as e:
            print(e)
        return False

    def get_thumbnail_url(self, obj):
        try:
            if obj.video.path:
                video_path = obj.video.path
                clip = VideoFileClip(video_path)
                thumbnail = clip.get_frame(2)  # Generate thumbnail at 2 seconds mark (can adjust as needed)

                # Save the thumbnail in the media directory
                thumbnail_name = 'thumbnail.png'  # Replace with the desired filename for the thumbnail
                thumbnail_path = os.path.join(settings.MEDIA_ROOT, thumbnail_name)
                clip.save_frame(thumbnail_path, t=2)  # Save the frame at 2 seconds as the thumbnail image

                # Generate the URL for the thumbnail
                thumbnail_url = f"{settings.MEDIA_URL}{thumbnail_name}"  # Assuming MEDIA_URL is properly configured

                return thumbnail_url

        except Exception as e:
            print(e)
            return ""


class ThreadPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThreadPost
        fields = '__all__'


# for showing likers
class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for object author info"""

    class Meta:
        model = User
        fields = ('username', 'image')


class CommentSerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = '__all__'

    def get_user_info(self, obj):
        user = obj.user
        encoded_image = base64.b64encode(user.image.read()).decode('utf-8')
        return {
            "fullname": user.firstname + " " + user.lastname,
            "encoded_image": encoded_image,
            "id": user.id,
        }


class CommentReplySerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField()

    class Meta:
        model = CommentReply
        fields = '__all__'

    def get_user_info(self, obj):
        user = obj.user
        encoded_image = base64.b64encode(user.image.read()).decode('utf-8')
        return {
            "fullname": user.firstname + " " + user.lastname,
            "encoded_image": encoded_image,
            "id": user.id,
        }


class ReportAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportAdmin
        fields = '__all__'
