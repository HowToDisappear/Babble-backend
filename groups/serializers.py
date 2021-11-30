from rest_framework import serializers

from accounts.serializers import AccountSerializer
from chats.serializers import GMSerializer
from .models import Group, Topic, Membership


class MembershipSerializer(serializers.ModelSerializer):
    account = AccountSerializer()

    class Meta:
        model = Membership
        fields = ['account', 'status']


class TopicSerializer(serializers.ModelSerializer):
    groupmessage_set = GMSerializer(many=True)

    class Meta:
        model = Topic
        fields = ['id', 'title', 'groupmessage_set']


class GroupSerializer(serializers.ModelSerializer):
    membership_set = MembershipSerializer(many=True)
    topic_set = TopicSerializer(many=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'topic_set', 'membership_set']
