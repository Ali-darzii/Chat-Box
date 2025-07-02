from django.utils.functional import cached_property
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView, UpdateAPIView
from rest_framework.views import APIView
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django_filters.rest_framework import DjangoFilterBackend
from django.db import IntegrityError as UniqueError
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema

from private_module.helper.filter import PrivateMessageFilter
from private_module.serializers import (
    ListPrivateBoxSerializer,
    SendPrivateMessageSerializer,
    PrivateMessageSerializer,
    EditPrivateMessageSerializer, PrivateMessageIsReadSerializer,

)
from private_module.models import PrivateBox, PrivateMessage
from utils.throttle import IsReadThrottle


class ListPrivateBox(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ListPrivateBoxSerializer

    def get_queryset(self):
        user = self.request.user
        return PrivateBox.objects.filter(
            Q(first_user=user) | Q(second_user=user)
        ).select_related("first_user", "second_user").order_by("-last_message")


class SendPrivateMessage(APIView):
    permission_classes = (IsAuthenticated,)
    @swagger_auto_schema(
        request_body=SendPrivateMessageSerializer,
        responses={200: '{"data": "message sent."}'},
        operation_description="Raises: 400, 403"
    )
    def post(self, request):
        serializer = SendPrivateMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        sender = request.user
        message = data.pop("message", None)
        file_url = data.pop("file", None)
        box_id = data.pop("box_id")
        receiver_id = data.pop("receiver_id")

        try:
            if box_id:
                box = PrivateBox.objects.get(pk=box_id)
            else:
                # rare case
                box = PrivateBox.objects.create(first_user=sender, second_user_id=receiver_id)
        except PrivateBox.DoesNotExist:
            raise NotFound
        except UniqueError:
            raise ValidationError

        if not (box.first_user != sender or box.second_user != sender):
            raise PermissionDenied

        box.last_message = timezone.now()
        box.save()
        PrivateMessage.objects.create(message=message, file=file_url, sender=sender, box=box)

        channel_layer = get_channel_layer()
        notification = {
            "type": "send_message",
            "message": {
                "type": "private",
                "box_id": box.id,
                "sender_id": sender.id,
                "message": message,
                "file": file_url,
            }
        }
        async_to_sync(channel_layer.group_send)(f"chat_{receiver_id}", notification)
        return Response({"data": "message sent."}, status=status.HTTP_200_OK)


class ListPrivateMessages(ListAPIView):
    serializer_class = PrivateMessageSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = PrivateMessageFilter

    @cached_property
    def auth_user(self):
        return self.request.user

    def get_queryset(self):
        try:
            box = PrivateBox.objects.get(pk=self.kwargs["box_id"])
        except box.DoesNotExist:
            raise NotFound
        sender = self.auth_user
        if not (sender == box.second_user or sender == box.first_user):
            raise PermissionDenied

        return PrivateMessage.objects.filter(box=box, is_delete=False).order_by("-created_at")

    def filter_queryset(self, queryset):
        messages = super().filter_queryset(queryset)
        user = self.auth_user
        is_read_data = []
        for message in messages:
            if message.sender != user and not message.is_read:
                message.is_read = True
                message.save()
                is_read_data.append(message)
        if is_read_data:
            serializer = PrivateMessageSerializer(data=is_read_data, many=True)
            channel_layer = get_channel_layer()
            notification = {
                "type": "send_message",
                "message": {
                    "type": "private_is_read",
                    "messages": serializer.data,
                }
            }
            private_box = messages[0].box
            receiver = private_box.receiver(user)
            async_to_sync(channel_layer.group_send)(f"chat_{receiver.id}", notification)

        return messages

class PrivateMessageIsRead(APIView):
    permission_classes = (IsAuthenticated,)
    throttle_classes = IsReadThrottle

    def put(self, request, message_id):
        serializer = PrivateMessageIsReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.request.user
        box_id = serializer.validated_data["box_id"]

        box = PrivateMessage.objects.filter(id__lte=message_id, box_id=box_id).exclude(sender=user)
        first_box = box.first()
        if first_box and (user != first_box.first_user or user != first_box.second_user):
            raise PermissionDenied
        box.update(is_read=True)
        return Response(status=status.HTTP_200_OK)





class EditPrivateMessage(UpdateAPIView):
    serializer_class = EditPrivateMessageSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return PrivateMessage.objects.filter(sender=self.request.user)
