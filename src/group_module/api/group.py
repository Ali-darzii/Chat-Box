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
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

from utils.throttle import IsReadThrottle
from group_module.helper.filter import GroupBoxAvatarFilter
from group_module.models import GroupBox, GroupBoxAvatar, GroupBoxMessage
from group_module.serializers import (
    CreateGroupBoxSerializer,
    DetailGroupBoxSerializer,
    EditGroubBoxUsersSerializer,
    EditGroupBoxAdminsSerializer,
    EditGroupBoxNameSerializer,
    GroupBoxAvatarViewSetSerializer,
    GroupMessageIsReadSerializer,
    GroupMessageOutputSerializer,
    GroupSendMessageSerializer,
)


class CreateGroupBox(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CreateGroupBoxSerializer


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

        return Response(data={"data": "message sent."})


class GroupMessageIsRead(APIView):
    permission_classes = IsAuthenticated
    throttle_classes = (IsReadThrottle,)
    @swagger_auto_schema(
        request_body=GroupMessageIsReadSerializer,
        responses={200: GroupMessageOutputSerializer},
    )
    def put(self, request, message_id):
        serializer = GroupMessageIsReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        receiver = request.user
        box_id = serializer.validated_data["box_id"]

        try:
            box = GroupBox.objects.get(pk=box_id)
            box_users = set(box.user.all())
            if receiver not in box_users:
                raise PermissionDenied
        except GroupBox.DoesNotExist:
            raise NotFound

        messages = GroupBoxMessage.objects.filter(
            id__lte=message_id, box=box, is_read=False, is_delete=False
        )
        if not messages.exists():
            raise NotFound
        update_messages = list(messages)
        messages.update(is_read=True)

        output_serializer = GroupMessageOutputSerializer(
            instance=update_messages, many=True
        )
        updated_messages = output_serializer.data
        channel_layer = get_channel_layer()
        notification = {
            "type": "send_message",
            "message": {
                "type": "group_is_read",
                "messages": updated_messages,
                "box_id": box.id,
            },
        }
        senders = box_users - receiver
        for sender in senders:
            async_to_sync(channel_layer.group_send)(f"chat_{sender.id}", notification)
        return Response(data=updated_messages, status=status.HTTP_200_OK)
