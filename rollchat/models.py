from django.db import models
from rolluser.models import User


# Create your models here.

def upload_to(instance, filename):
    return 'chat/{filename}'.format(filename=filename)


class Chat(models.Model):
    content = models.TextField(default="")
    imaage = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey('ChatRoom', on_delete=models.CASCADE)


class ChatRoom(models.Model):
    name = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.name
