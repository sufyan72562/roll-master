from django.db import models
from rolluser.models import User
from django.utils.timezone import now


# Create your models here.
def upload_to(instance, filename):
    return 'post/images/{filename}'.format(filename=filename)


def upload_too(instance, filename):
    return 'post/videos/{filename}'.format(filename=filename)


def upload_tooo(instance, filename):
    return 'post/voice/{filename}'.format(filename=filename)


class Posts(models.Model):
    caption = models.TextField(blank=True)
    image = models.TextField(blank=True)
    video = models.FileField(upload_to=upload_too, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_thread = models.BooleanField(default=0)
    likes = models.ManyToManyField(User,
                                   related_name="likers",
                                   blank=True,
                                   symmetrical=False)
    views = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    objects = models.Manager()


class ThreadPost(models.Model):
    caption = models.TextField(blank=True)
    image = models.TextField(blank=True)
    post_id = models.ForeignKey(Posts, on_delete=models.CASCADE, blank=True)
    objects = models.Manager()


class Comment(models.Model):
    comment = models.TextField(blank=True)
    voice = models.FileField(upload_to=upload_tooo, blank=True)
    posts = models.ForeignKey(Posts, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_reply = models.BooleanField(default=0)
    timestump = models.DateTimeField(default=now)
    objects = models.Manager()


class CommentReply(models.Model):
    comment = models.TextField(blank=True)
    voice = models.FileField(upload_to=upload_tooo, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True)
    timestump = models.DateTimeField(default=now)
    objects = models.Manager()


class ReportAdmin(models.Model):
    user = models.ForeignKey(User, related_name="user", on_delete=models.CASCADE, null=True)
    reportuser = models.ForeignKey(User, related_name="reportuser", on_delete=models.CASCADE, null=True)
    reportpost = models.ForeignKey(Posts, on_delete=models.CASCADE, null=True)
    reportcomment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True)
    reportreply = models.ForeignKey(CommentReply, on_delete=models.CASCADE, null=True)
