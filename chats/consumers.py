import json

from django.contrib.sessions.models import Session
from django.shortcuts import get_object_or_404

from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Client, DirectMessage, GroupMessage
from accounts.models import Account, Contact
from groups.models import Group, Topic
from .serializers import DMSerializer, GMSerializer


class ClientConsumer(WebsocketConsumer):
    def connect(self):
        """
        accept ws connection, notify of online status
        """
        self.account = Account.objects.get(user=self.scope["user"])
        self.channel_layer = get_channel_layer()
        Client.objects.create(account=self.account, channel_name=self.channel_name)
        for group in self.account.group_set.all():
            async_to_sync(self.channel_layer.group_add)(
                f'{group.id}',
                self.channel_name
            )
        self.accept()
        self.notify(status='online')

    def disconnect(self, close_code):
        """
        notify that we go offline, disconnect from ws
        """
        self.notify('offline')
        Client.objects.filter(channel_name=self.channel_name).delete()
        for group in self.account.group_set.all():
            async_to_sync(self.channel_layer.group_discard)(
                f'{group.id}',
                self.channel_name
            )
        if not self.account.keep_signed_in:
            Session.objects.get(pk=self.scope['cookies']['sessionid']).delete()

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if text_data_json['type'] == 'direct.message':
            acc_id = text_data_json['account']
            cont = get_object_or_404(Account, id=acc_id)
            msg = text_data_json['message']
            msg = DirectMessage.objects.create(
                sender=self.account,
                recipient=cont,
                text=msg
            )
            serializer = DMSerializer(msg)
            self.send(text_data=json.dumps({
                'type': 'direct.message',
                'content': serializer.data
            }))
            # qs = Client.objects.filter(account=cont)
            # client = qs[0] if qs else None
            client = cont.client_set.all()
            if client:
                async_to_sync(self.channel_layer.send)(client[0].channel_name, {
                    'type': 'direct.message',
                    'content': serializer.data
                })
        elif text_data_json['type'] == 'group.message':
            group_id = text_data_json['group']
            group = get_object_or_404(Group, id=group_id)
            topic_id = text_data_json['topic']
            topic = get_object_or_404(Topic, id=topic_id)
            msg = text_data_json['message']
            msg = GroupMessage.objects.create(
                sender=self.account,
                recipient=group,
                topic=topic,
                text=msg
            )
            serializer = GMSerializer(msg)
            async_to_sync(self.channel_layer.group_send)(
                f'{group.id}',
                {
                    'type': 'group.message',
                    'content': serializer.data
                }
            )
        elif text_data_json['type'] == 'chat.read':
            acc_id = text_data_json['account']
            cont = get_object_or_404(Account, id=acc_id)
            messages = DirectMessage.objects.filter(recipient=self.account,
                                                    sender=cont,
                                                    read=False)
            for msg in messages:
                msg.read = True
                msg.save()

        elif text_data_json['type'] == 'update':
            structure = text_data_json['structure']
            id = text_data_json['id']
            if structure == 'dm':
                client = Client.objects.filter(account=id)
                if client:
                    async_to_sync(self.channel_layer.send)(client[0].channel_name, {
                        'type': 'update.dm',
                    })
                    async_to_sync(self.channel_layer.send)(client[0].channel_name, {
                        'type': 'status.message',
                        'content': {
                            'account': f"{self.account.id}",
                            'status': 'online'
                        }
                    })
                    async_to_sync(self.channel_layer.send)(self.channel_name, {
                        'type': 'status.message',
                        'content': {
                            'account': f"{client[0].account.id}",
                            'status': 'online'
                        }
                    })
            elif structure == 'gm':
                group = get_object_or_404(Group, id=id)
                members = group.members.all()
                for member in members:
                    client = Client.objects.filter(account=member)
                    if client:
                        async_to_sync(self.channel_layer.send)(client[0].channel_name, {
                            'type': 'update.gm',
                        })
            self.send(text_data=json.dumps({
                'type': f'update.{structure}',
            }))

    def status_message(self, event):
        self.send(text_data=json.dumps({
            'type': 'status.message',
            'content': event['content']
        }))

    def direct_message(self, event):
        self.send(text_data=json.dumps({
            'type': 'direct.message',
            'content': event['content']
        }))

    def group_message(self, event):
        self.send(text_data=json.dumps({
            'type': 'group.message',
            'content': event['content']
        }))

    def update_dm(self, event):
        self.send(text_data=json.dumps({
            'type': 'update.dm',
        }))

    def update_gm(self, event):
        self.send(text_data=json.dumps({
            'type': 'update.gm',
        }))

    def notify(self, status):
        """
        notify every contact online that we go online/ offline,
        notify ourselves about every contact that is online
        """
        contacts = set(self.account.contacts.all())
        for group in self.account.group_set.all():
            for member in group.members.all():
                contacts.add(member)
        contacts.discard(self.account)
        for contact in contacts:
            client = contact.client_set.all()
            if client:
                async_to_sync(self.channel_layer.send)(client[0].channel_name, {
                    'type': 'status.message',
                    'content': {
                        'account': f"{self.account.id}",
                        'status': status
                    }
                })
                if status == 'online':
                    async_to_sync(self.channel_layer.send)(self.channel_name, {
                        'type': 'status.message',
                        'content': {
                            'account': f"{client[0].account.id}",
                            'status': status
                        }
                    })
        async_to_sync(self.channel_layer.send)(self.channel_name, {
            'type': 'status.message',
            'content': {
                'account': f"{self.account.id}",
                'status': status
            }
        })
