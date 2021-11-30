from django.db import models

from accounts.models import Account


class Group(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(Account, through='Membership')

    def __str__(self):
        return self.name


class Topic(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class Membership(models.Model):
    MEMBERSHIP_STATUSES = [
        (1, 'participant'),
        (2, 'administrator'),
        (3, 'invitee')
    ]
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    status = models.IntegerField(choices=MEMBERSHIP_STATUSES)
