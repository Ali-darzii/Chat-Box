from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, ListModelMixin, DestroyModelMixin
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.response import Response

from group_module.helper.filter import GroupBoxAvatarFilter
from group_module.models import GroupBox, GroupBoxAvatar, GroupBoxMessage
from group_module.serializers import (
    CreateGroupBoxSerializer,
    DetailGroupBoxSerializer,
    EditGroubBoxUsersSerializer,
    EditGroupBoxAdminsSerializer,
    EditGroupBoxNameSerializer,
    GroupBoxAvatarViewSetSerializer,
    GroupSendMessageSerializer,
)


class CreateGroupBox(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CreateGrouobjectpBoxSerializer


class DetailGroupBox(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = DetailGroupBoxSerializer

    def get_queryset(self):
        return GroupBox.objects.filter(users=self.request.user)


class EditGroupBoxName(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EditGroupBoxNameSerializer

    def get_queryset(self):
        return GroupBox.objects.filter(admins=self.request.user)


class EditGroupBoxAdmins(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EditGroupBoxAdminsSerializer

    def get_queryset(self):
        return GroupBox.objects.filter(admins=self.request.user)


class EditGroupBoxUsers(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EditGroubBoxUsersSerializer

    def get_queryset(self):
        return GroupBox.objects.filter(admins=self.request.user)


class GroupBoxAvatarViewSet(
    GenericViewSet, CreateModelMixin, ListModelMixin, DestroyModelMixin
):
    permission_classes = (IsAuthenticated,)
    serializer_class = GroupBoxAvatarViewSetSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = GroupBoxAvatarFilter

    def get_queryset(self):
        if self.request.method == "GET":
            return GroupBoxAvatar.objects.filter(group__users=self.request.user)
        return GroupBoxAvatar.objects.filter(group__admins=self.request.user)

    def filter_queryset(self, queryset):
        if self.request.method == "GET":
            return super().filter_queryset(queryset)
        return queryset


class SendGroupMessage(APIView):
    permission_classes = (IsAuthenticated,)
    
    
    def post(self, request):
        serializer = GroupSendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        sender = request.sender
        message = data.get("message", None)
        file_url = data.get("file", None)
        box_id = data.get("box_id")
        
        try:
            box = GroupBox.objects.get(pk=box_id).prefetch_related("users")
        except GroupBox.DoesNotExist:
            raise NotFound
        box_users = set(box.users.all())
        if not sender in box_users:
            raise PermissionDenied
        
        GroupBoxMessage.objects.create(**data, sender=sender)
        box.last_message = timezone.now()
        box.save()
        
        
        channel_layer = get_channel_layer()
        notification = {
            "type": "send_message",
            "message": {
                "type": "group",
                "box_id": box.id,
                "sender_id": sender.id,
                "message": message,
                "file": file_url,
            },
        }
        receivers = box_users - set(sender) 
        for receiver in receivers:
            async_to_sync(channel_layer.group_send)(f"chat_{receiver.id}", notification)
        
        return Response(data={"data":"message sent."})
        