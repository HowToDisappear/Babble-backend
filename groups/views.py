from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from accounts.models import Account
from .models import Group, Topic, Membership
from .serializers import GroupSerializer


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def group(request, group_id):
    """ add/remove members, delete group """
    # create decorator for administrator check: if True else 403
    own_acc = get_object_or_404(Account, user=request.user)
    group = get_object_or_404(own_acc.group_set, id=group_id)
    admin = Membership.objects.get(group=group, account=own_acc).status == 2
    if request.method == 'POST':
        if request.data['action'] == 'add_member':
            if admin:
                acc = get_object_or_404(Account, id=request.data['account'])
                Membership.objects.create(group=group, account=acc, status=3)
                return Response(status=201)
            else:
                return Response(status=403)
        elif request.data['action'] == 'remove_member':
            if admin:
                acc = get_object_or_404(Account, id=request.data['account'])
                membership = get_object_or_404(Membership, group=group, account=acc)
                membership.delete()
                return Response(status=204)
            else:
                membership = get_object_or_404(Membership, group=group, account=own_acc)
                membership.delete()
                return Response(status=204)
        elif request.data['action'] == 'change_status':
            membership = get_object_or_404(Membership, group=group, account=own_acc)
            if membership.status == 3:
                membership.status = 1
                membership.save()
                return Response(status=201)
            else:
                return Response(status=400)
    elif request.method == 'DELETE':
        if admin:
            group.delete()
            return Response(status=204)
        else:
            return Response(status=403)
    return Response(status=400)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def groups(request):
    """ view/ add groups """
    acc = get_object_or_404(Account, user=request.user)
    if request.method == 'GET':
        groups = acc.group_set.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        name = request.data['name']
        group = Group.objects.create(name=name)
        Membership.objects.create(group=group, account=acc, status=2)
        return Response(status=201)
        # Topic.objects.create(group=group, title='General')


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def topics(request, group_id):
    """ view/ add topics """
    acc = get_object_or_404(Account, user=request.user)
    group = get_object_or_404(acc.group_set, id=group_id)
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        admin = Membership.objects.filter(group=group, account=acc, status=2)
        if admin:
            title = request.data['title']
            Topic.objects.create(group=group, title=title)
            return Response(status=201)
        else:
            return Response(status=403)
