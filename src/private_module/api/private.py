from django.http import Http404
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView, ListAPIView
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from private_module.helper.filter import PrivateMessageFilter

from utils.response import ErrorResponses as error
from private_module.serializers import (
    ListPrivateBoxSerializer,
    SendPrivateMessageSerializer,
    PrivateMessageSerializer,

)
from private_module.models import PrivateBox, PrivateMessage


class ListPrivateBox(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ListPrivateBoxSerializer

    def get_queryset(self):
        return PrivateBox.objects.filter(
            Q(first_user=self.request.user) | Q(second_user=self.request.user)
        ).order_by("-last_message")


class SendPrivateMessage(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, box_id):
        serializer = SendPrivateMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        sender = request.user
        message = data.get("message", "")
        file_url = data.get("file", "")

        try:
            box, _ = PrivateBox.objects.get_or_create(
                pk=box_id,
                defaults={"first_user": request.user, "second_user": sender}
            )
        except PrivateBox.DoesNotExist:
            raise Http404


        if not (box.first_user != sender or box.second_user != sender):
            return Response(error.BAD_REQUEST, status=status.HTTP_406_NOT_ACCEPTABLE)
        if box.first_user == sender:
            receiver = box.second_user
        else:
            receiver = box.first_user


        box.last_message = timezone.now()
        box.save()
        PrivateMessage.objects.create(message=message, file=file_url, sender=sender, box=box)

        channel_layer = get_channel_layer()
        notification = {
            "type": "send_message",
            "message": {
                "box_id": box_id,
                "sender_id": sender.id,
                "message": message,
                "file": file_url,
            }
        }
        async_to_sync(channel_layer.group_send)(f"chat_{receiver.id}", notification)
        return Response({"data": "message sent."}, status=status.HTTP_200_OK)


class GetPrivateMessages(ListAPIView):
    serializer_class = PrivateMessageSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = PrivateMessageFilter

    def get_queryset(self):
        try:
            box = PrivateBox.objects.get(pk=self.kwargs["box_id"])
        except box.DoesNotExist:
            raise Http404
        sender = self.request.user
        if not (sender == box.second_user or sender == box.first_user):
            raise PermissionDenied

        return PrivateMessage.objects.filter(box=box).order_by("-created_at")


class EditPrivateMessage(APIView):
    def put(self, request, box_id: str):
        pass
