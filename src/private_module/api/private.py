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
    EditPrivateMessageSerializer,
    PrivateMessageIsReadSerializer,
    PrivateMessageOutputSerializer,
)
from private_module.models import PrivateBox, PrivateMessage
from utils.throttle import IsReadThrottle


class ListPrivateBox(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ListPrivateBoxSerializer

    def get_queryset(self):
        user = self.request.user
        return (
            PrivateBox.objects.filter(Q(first_user=user) | Q(second_user=user))
            .select_related("first_user", "second_user")
            .order_by("-last_message")
        )


class SendPrivateMessage(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        request_body=SendPrivateMessageSerializer,
        responses={201: '{"data": "message sent."}'},
        operation_description="Raises: 400, 403",
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
                box = PrivateBox.objects.create(
                    first_user=sender, second_user_id=receiver_id
                )
        except PrivateBox.DoesNotExist:
            raise NotFound
        except UniqueError:
            raise ValidationError

        if not box.is_user_included(sender):
            raise PermissionDenied

        PrivateMessage.objects.create(
            message=message, file=file_url, sender=sender, box=box
        )
        box.last_message = timezone.now()
        box.save()

        channel_layer = get_channel_layer()
        notification = {
            "type": "send_message",
            "message": {
                "type": "private",
                "box_id": box.id,
                "sender_id": sender.id,
                "message": message,
                "file": file_url,
            },
        }
        async_to_sync(channel_layer.group_send)(f"chat_{receiver_id}", notification)
        return Response({"data": "message sent."}, status=status.HTTP_201_CREATED)


class ListPrivateMessages(ListAPIView):
    serializer_class = PrivateMessageSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = PrivateMessageFilter

    def get_queryset(self):
        try:
            box = PrivateBox.objects.get(pk=self.kwargs["box_id"])
            if not box.is_user_included(self.request.user):
                raise PermissionDenied
        except box.DoesNotExist:
            raise NotFound
        return PrivateMessage.objects.filter(box=box, is_delete=False).order_by(
            "-created_at"
        )


class PrivateMessageIsRead(APIView):
    permission_classes = (IsAuthenticated,)
    throttle_classes = (IsReadThrottle,)
    """
    - API will update is_read=True until reach to given message.
    - API will send updated messages in Response.
    - API will send updated messages for receiver user.
    """

    @swagger_auto_schema(
        request_body=PrivateMessageIsReadSerializer,
        responses={200: PrivateMessageOutputSerializer},
    )
    def put(self, request, message_id):
        serializer = PrivateMessageIsReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        receiver = self.request.user
        box_id = serializer.validated_data["box_id"]

        try:
            box = PrivateBox.objects.get(pk=box_id)
            if not box.is_user_included(receiver):
                raise PermissionDenied
        except PrivateBox.DoesNotExist:
            raise NotFound
        sender = box.receiver(receiver)

        messages = PrivateMessage.objects.filter(
            id__lte=message_id, box=box, is_read=False, is_delete=False
        ).exclude(sender=receiver)
        if not messages.exists():
            raise NotFound
        update_messages = list(messages)
        messages.update(is_read=True)

        output_serializer = PrivateMessageOutputSerializer(update_messages, many=True)
        updated_messages = output_serializer.data
        channel_layer = get_channel_layer()
        notification = {
            "type": "send_message",
            "message": {
                "type": "private_is_read",
                "messages": updated_messages,
                "box_id": box.id,
            },
        }
        async_to_sync(channel_layer.group_send)(f"chat_{sender.id}", notification)
        return Response(data=updated_messages, status=status.HTTP_200_OK)


class EditPrivateMessage(UpdateAPIView):
    serializer_class = EditPrivateMessageSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return PrivateMessage.objects.filter(sender=self.request.user)
