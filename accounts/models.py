import os
from django.db import models
from django.contrib.auth import get_user_model


def user_path(instance, filename):
    return f'accounts/{filename}'


class Account(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    username = models.CharField(max_length=30, blank=True, null=True)
    about = models.CharField(max_length=150, blank=True, null=True)
    temp_email = models.EmailField(max_length=100, blank=True, null=True)
    contacts = models.ManyToManyField('self',
                                      through='Contact',
                                      through_fields=('from_account', 'to_account'))
    image = models.ImageField(upload_to=user_path, blank=True, null=True)
    keep_signed_in = models.BooleanField(default=True)

    def __str__(self):
        return self.username


class Contact(models.Model):
    CONTACT_STATUSES = [
        (1, 'active'),
        (2, 'blocked'),
        (3, 'invited'),
        (4, 'friend'),
    ]
    from_account = models.ForeignKey(Account,
                                     on_delete=models.CASCADE,
                                     related_name='contact_list')
    to_account = models.ForeignKey(Account,
                                   on_delete=models.CASCADE,
                                   related_name='contact_of')
    inviter = models.ForeignKey(Account,
                                on_delete=models.CASCADE,
                                related_name='contact_inviter',
                                blank=True,
                                null=True)
    status = models.IntegerField(choices=CONTACT_STATUSES)
