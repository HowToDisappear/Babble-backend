import io
from PIL import Image
from uuid import uuid4

from django.core.files import File
from django.core.files.base import ContentFile

from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.db.models import Q
from django.contrib.auth.hashers import check_password

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from django.views.decorators.csrf import csrf_exempt

from chats.models import DirectMessage

from .models import Account, Contact
from .serializers import (UserSerializer,
                          AccountSerializer,
                          ThroughSerializer,
                          ContactSerializer)


token_generator = PasswordResetTokenGenerator()


ACTIVATE_SUBJ = "Confirm registration at Babble"
ACTIVATE_BODY = """<p>Hello, please confirm your registration at Babble: \
    <a href='http://127.0.0.1:8000/api/accounts/activate/{uid}/{token}'>confirm<a></p>"""


CHANGE_SUBJ = "Confirm email change at Babble"
CHANGE_BODY = """<p>Hello, please confirm email change at Babble: \
    <a href='http://127.0.0.1:8000/api/accounts/update/{uid}/{token}'>confirm<a></p>"""



def send_mail(subject, body, to):
    msg = EmailMessage(
        subject=subject,
        body=body,
        to=to,
    )
    msg.content_subtype = 'html'
    msg.send()


# def send_mail(subject, body, user, token):
#     # turns uid to byte string, then encodes to base64 string to embed into url
#     uid = urlsafe_base64_encode(force_bytes(user.id))
#     msg = EmailMessage(
#         subject=subject,
#         body=body.format(username=user.username, uid=uid, token=token),
#         to=[user.email],
#     )
#     msg.content_subtype = 'html'
#     msg.send()


@api_view(['POST'])
def signup(request):
    """ Creates new inactive user and sends confirmation email with token """
    email = request.data['email']
    username = request.data['username']
    password = request.data['password']
    if get_user_model().objects.filter(username=email):
        return Response(status=403)
    serializer = UserSerializer(data={
        'email': email,
        'username': email,
        'password': password
    })
    if serializer.is_valid():
        user = serializer.save(is_active=False)
        Account.objects.create(user=user, username=username)
        uid = urlsafe_base64_encode(force_bytes(user.id))
        token = token_generator.make_token(user)
        send_mail(subject=ACTIVATE_SUBJ,
                  body=ACTIVATE_BODY.format(uid=uid, token=token),
                  to=[user.email])
        return Response(status=201)
    return Response(serializer.errors, status=400)


@api_view(['GET'])
def activate(request, uid, token):
    # decodes base64 to byte string and back to uid string
    uid = force_str(urlsafe_base64_decode(uid))
    try:
        user = get_user_model().objects.get(id=uid)
    except:
        return Response(status=404)
    if token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('/')
    else:
        return Response(status=400)


@api_view(['GET'])
def update(request, uid, token):
    # decodes base64 to byte string and back to uid string
    uid = force_str(urlsafe_base64_decode(uid))
    user = get_object_or_404(get_user_model(), id=uid)
    acc = get_object_or_404(Account, user=user)
    if token_generator.check_token(user, token):
        user.username = acc.temp_email
        user.email = acc.temp_email
        acc.temp_email = ''
        user.save()
        acc.save()
        return redirect('/')
    else:
        return Response(status=400)


@api_view(['POST'])
def signin(request):
    """ sign in a user """
    username = request.data['username']
    password = request.data['password']
    keep_signed_in = True if request.POST['keep_signed_in'] == 'true' else False
    user = authenticate(request, username=username, password=password)
    print(user)
    if user is not None:
        login(request, user)
        acc = get_object_or_404(Account, user=user)
        acc.keep_signed_in = keep_signed_in
        acc.save()
        serializer = AccountSerializer(acc)
        return Response(serializer.data)
    else:
        return Response(status=401)


@api_view(['GET'])
def signout(request):
    logout(request)
    return Response(status=200)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def account(request):
    """ view/ change/ delete own account """
    user = request.user
    acc = get_object_or_404(Account, user=user)
    if request.method == 'GET':
        serializer = AccountSerializer(acc)
        return Response(serializer.data)
    if request.method == 'PUT':
        if 'avatar' in request.data:
            if not request.data['avatar']:
                acc.image.delete()
                serializer = AccountSerializer(acc)
                return Response(serializer.data)
            else:
                if acc.image:
                    acc.image.delete()
                f = request.data['avatar'].file.getvalue()
                acc.image.save(f'{uuid4()}.png', ContentFile(f))
                serializer = AccountSerializer(acc)
                return Response(serializer.data)
        elif 'username' in request.data and 'about' in request.data:
            acc.username = request.data['username']
            acc.about = request.data['about']
            acc.save()
            serializer = AccountSerializer(acc)
            return Response(serializer.data)
        elif 'old_password' in request.data and 'new_password' in request.data:
            if check_password(request.data['old_password'], user.password):
                user.set_password(request.data['new_password'])
                user.save()
                return Response(status=204)
            else:
                return Response(status=401)
        elif 'current_password' in request.data and 'new_email' in request.data:
            if check_password(request.data['current_password'], user.password):
                acc.temp_email = request.data['new_email']
                acc.save()
                uid = urlsafe_base64_encode(force_bytes(user.id))
                token = token_generator.make_token(user)
                send_mail(subject=CHANGE_SUBJ,
                          body=CHANGE_BODY.format(uid=uid, token=token),
                          to=[acc.temp_email])
                return Response(status=201)

            else:
                return Response(status=401)
        else:
            return Response(status=400)
    if request.method == 'DELETE':
        if 'current_password' in request.data:
            if check_password(request.data['current_password'], user.password):
                user.delete()
                return Response(status=204)
        else:
            return Response(status=400)
    return Response(status=405)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def contacts(request):
    """ view all contacts or add a new contact """
    user = request.user
    acc = get_object_or_404(Account, user=user)
    if request.method == 'GET':
        serializer = ContactSerializer(acc)
        return Response(serializer.data)
    elif request.method == 'POST':
        to_acc = int(request.data['to_account'])
        status = int(request.data['status'])
        to_acc = get_object_or_404(Account, id=to_acc)
        Contact.objects.create(from_account=acc, to_account=to_acc, status=status)
        Contact.objects.create(from_account=to_acc, to_account=acc, status=status)
        return Response(status=201)
    return


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def contact(request, cont_id):
    """ view/update/delete specific contact """
    user = request.user
    acc = get_object_or_404(Account, user=user)
    cont = get_object_or_404(Account, id=cont_id)
    if request.method == 'GET':
        serializer = AccountSerializer(cont)
        return Response(serializer.data)
    elif request.method == 'PUT':
        relation = get_object_or_404(Contact, from_account=acc, to_account=cont)
        serializer = ThroughSerializer(instance=relation, data=request.data)
        if serializer.is_valid():
            serializer.save(from_account=acc, to_account=cont)
            return Response(status=204)
    elif request.method == 'DELETE':
        messages = DirectMessage.objects.filter(Q(sender=acc, recipient=cont) |
                                                Q(sender=cont, recipient=acc))
        messages.delete()
        rel1 = get_object_or_404(Contact, from_account=acc, to_account=cont)
        rel1.delete()
        rel2 = get_object_or_404(Contact, from_account=cont, to_account=acc)
        rel2.delete()
        return Response(status=204)
