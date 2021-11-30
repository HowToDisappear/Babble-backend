import json

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, get_user_model

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from accounts.models import Account, Contact
from accounts.serializers import AccountSerializer
from .models import DirectMessage, GroupMessage
from .serializers import DMSerializer

# @api_view(['GET'])
# def chat(request, cont_id):
#     user = get_object_or_404(Account, user=request.user)
#     # user = get_user_model().objects.get(username='john@mail.com')
#     # user = get_object_or_404(Account, user=user)
#     contact = get_object_or_404(Account, id=cont_id)
#     messages = Message.objects.filter(Q(sender=user, recipient=contact) |
#                                       Q(sender=contact, recipient=user))
#     serializer = MessageSerializer(messages, many=True)
#     return Response(serializer.data)


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def chats(request):
#     user = get_object_or_404(Account, user=request.user)
#     # user = get_user_model().objects.get(username='john@mail.com')
#     # user = get_object_or_404(Account, user=user)
#     contacts = user.contacts.all()
#     chats = {}
#     for contact in contacts:
#         messages = DirectMessage.objects.filter(Q(sender=user, recipient=contact) |
#                                                 Q(sender=contact, recipient=user))
#         serializer = MessageSerializer(messages, many=True)
#         chats[contact.id] = serializer.data
#     return Response(chats)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def direct_messages(request):
    """ view direct messages and respective contacts (excluding blocked) """
    acc = get_object_or_404(Account, user=request.user)
    contacts = acc.contacts.all()
    chats_native = {}
    cont_list = []

    for contact in contacts:
        contact_through = Contact.objects.get(from_account=acc, to_account=contact)
        if contact_through.status == 2:
            continue
        cont_list.append(contact)
        messages = DirectMessage.objects.filter(Q(sender=acc, recipient=contact) |
                                                Q(sender=contact, recipient=acc))
        chats_native[contact.id] = DMSerializer(messages, many=True).data

    chats_native = json.loads(json.dumps(chats_native))
    contacts_native = json.loads(json.dumps(AccountSerializer(cont_list, many=True).data))
    for contact in contacts_native:
        contact['directmessage_set'] = chats_native[str(contact['id'])]

    return Response(contacts_native)


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def direct_messages(request):
#     """ view direct messages and respective contacts (excluding blocked) """
#     acc = get_object_or_404(Account, user=request.user)
#     contacts = acc.contacts.all()
#     chats_native = {}
#     contacts_list = []
#
#     for contact in contacts:
#         contact_through = Contact.objects.get(from_account=acc, to_account=contact)
#         if contact_through.status == 2:
#             continue
#         contacts_list.append(contact)
#         messages = DirectMessage.objects.filter(Q(sender=acc, recipient=contact) |
#                                                 Q(sender=contact, recipient=acc))
#         chats_native[contact.id] = DMSerializer(messages, many=True).data
#
#     contacts_native = AccountSerializer(contacts_list, many=True).data
#     return Response({
#         'chats': chats_native,
#         'contacts': contacts_native
#     })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def group_messages(request):
    pass




# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def direct_messages(request):
#     """ view direct messages and respective contacts (excluding blocked) """
#     acc = get_object_or_404(Account, user=request.user)
#     messages = DirectMessage.objects.filter(Q(sender=acc) | Q(recipient=acc))
#
#     chats = {}
#     for msg in messages:
#         if msg.sender != acc:
#             if msg.sender in chats:
#                 chats[msg.sender].append(msg)
#             else:
#                 chats[msg.sender] = [msg]
#         else:
#             if msg.recipient in chats:
#                 chats[msg.recipient].append(msg)
#             else:
#                 chats[msg.recipient] = [msg]
#
#     contacts = set()
#     chats_native = {}
#     for contact, chat in chats.items():
#         cont = Contact.objects.filter(from_account=acc, to_account=contact)
#         if cont and cont[0].status == 2:
#             continue
#         contacts.add(contact)
#         chats_native[contact.id] = DMSerializer(chat, many=True).data
#
#     contacts_native = AccountSerializer(contacts, many=True).data
#     resp = {
#         'chats': chats_native,
#         'contacts': contacts_native
#     }
#     return Response(resp)
