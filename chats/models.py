from django.db import models
from django.conf import settings

from accounts.models import Account
from groups.models import Group, Topic


class Client(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    channel_name = models.CharField(max_length=100)


class DirectMessage(models.Model):
    sender = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='dm_sender')
    recipient = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='dm_recipient')
    timestamp = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=800)
    read = models.BooleanField(default=False)


class GroupMessage(models.Model):
    sender = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='gm_sender')
    recipient = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='gm_recipient')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=800)
    read_status = models.ManyToManyField(Account, through='ReadStatus')


class ReadStatus(models.Model):
    group_message = models.ForeignKey(GroupMessage, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    read = models.BooleanField(default=False)
