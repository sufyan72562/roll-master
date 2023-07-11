from django.db import models
from rolluser.models import User


class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')

    def __str__(self):
        return f'Conversation {self.pk}'

    objects = models.Manager()


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    image = models.TextField(blank=True, null=True)
    is_seen = models.BooleanField(default=False)

    def __str__(self):
        return f'Message {self.pk}'

    objects = models.Manager()
