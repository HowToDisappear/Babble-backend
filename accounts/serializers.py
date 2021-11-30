from django.contrib.auth import get_user_model

from rest_framework import serializers
from .models import Account, Contact


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name',]
        extra_kwargs = {
            'id': {'read_only': True},
            'first_name': {'read_only': True},
            'last_name': {'read_only': True},
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = get_user_model().objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.is_active = False
        user.save()
        return user


class AccountSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Account
        fields = ['id', 'user', 'username', 'about', 'image']
        extra_kwargs = {
            'id': {'read_only': True},
            'image': {'read_only': True}
        }


class ThroughSerializer(serializers.ModelSerializer):
    to_account = AccountSerializer(required=False)

    class Meta:
        model = Contact
        fields = ['from_account', 'to_account', 'status']
        extra_kwargs = {
            'from_account': {'write_only': True, 'required': False},
        }


class ContactSerializer(serializers.ModelSerializer):
    contact_list = ThroughSerializer(many=True)

    class Meta:
        model = Account
        fields = ['contact_list']
