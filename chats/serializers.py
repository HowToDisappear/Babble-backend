from rest_framework import serializers

from .models import DirectMessage, GroupMessage


class DMSerializer(serializers.ModelSerializer):
    class Meta:
        model = DirectMessage
        fields = ['id', 'sender', 'recipient', 'timestamp', 'text', 'read']



class GMSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMessage
        fields = ['id', 'sender', 'recipient', 'topic', 'timestamp', 'text', 'read_status']
