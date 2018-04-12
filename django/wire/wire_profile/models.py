from django.db import models
from django.contrib.auth.models import User


class Message(models.Model):
    message_text = models.CharField(max_length=280)
    created = models.DateTimeField('created')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.message_text


class Follow(models.Model):
    follower_id = models.ForeignKey(User, related_name='follower_user', on_delete=models.CASCADE)
    following_id = models.ForeignKey(User, related_name='followed_user', on_delete=models.CASCADE)
