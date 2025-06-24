from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView, ListAPIView
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime, timedelta
from django.utils import timezone

from utils.utils import timestamp_to_real_time
from utils.response import ErrorResponses as error
from private_module.serializers import (
    CreatePrivateBoxSerializer,
    ListPrivateBoxSerializer,
    SendPrivateMessageSerializer,
    GetPrivateMessagesInputSerialzier,
    PrivateBoxMessagesSerialzier,
    EditPrivateMessageInputSerializer,

)
from private_module.models import PrivateBox, PrivateMessage



class ListPrivateBox(ListAPIView):
    """
    - List of users are in the same Box but authenticated user is excluded.
    """
    
    permission_classes = (IsAuthenticated,)
    serializer_class = ListPrivateBoxSerializer

    def get_queryset(self):
        return PrivateBox.objects.filter(
            Q(first_user=self.request.user) |Q(second_user=self.request.user)
        ).order_by("-last_message")
    

class CreatePrivateBox(CreateAPIView):
    """ 
    - We will use this if it's first message.
    - Then we call SendPrivateMessage EndPoint.
    - Same authenticad user can't make room with him self
    """
    
    permission_classes = (IsAuthenticated,)
    serializer_class = CreatePrivateBoxSerializer
    
    def perform_create(self, serializer):
        serializer.save(first_user=self.request.user)
    

class SendPrivateMessage(APIView):
    """
    - With sending box_id you send message and file.
    - Authenticated user must be in that box.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, box_id):
        serializer = SendPrivateMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        sender = request.user
        message = data.get("message", "")
        file_url = data.get("file", "")
        
        try:
            box = PrivateBox.objects.get(pk=box_id)
            if not (box.first_user != sender or box.second_user != sender):
                return Response(error.BAD_REQUEST, status=status.HTTP_406_NOT_ACCEPTABLE)
            box.last_message = timezone.now()
            box.save()
        except:
            return Response(error.OBJECT_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)

        PrivateMessage.objects.create(message=message, file=file_url, sender=sender, box=box)
        if box.first_user == sender:
            receiver = box.second_user
        else:
            receiver = box.first_user

        channel_layer = get_channel_layer()
        print(channel_layer)
        notification = {
            "type":"send_message",
            "message": {
                "box_id": box_id,
                "sender_id": sender.id,
                "message": message,
                "file": file_url,
            }
        }
        async_to_sync(channel_layer.group_send)(f"chat_{receiver.id}", notification)
        return Response({"data":"message sent."}, status=status.HTTP_200_OK)


class GetPrivateMessages(APIView):
    """
    - Depends on query parameters you can get what ever you want from messages
    - Time of every server is 3.30 a head.
    """
    
    permission_classes = (IsAuthenticated, )


    def get(self, request, box_id):
        serializer = GetPrivateMessagesInputSerialzier(data=request.query_params.dict())
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        sender = request.user
        try:
            box = PrivateBox.objects.get(pk=box_id)
            if not(box.first_user != sender or box.second_user != sender):
                return Response(error.BAD_REQUEST, status=status.HTTP_406_NOT_ACCEPTABLE)
        except PrivateBox.DoesNotExist:
            return Response(error.OBJECT_NOT_FOUND, status=status.HTTP_400_BAD_REQUEST)
        time_diff = timedelta(hours=3, minutes=30)
        start = timestamp_to_real_time(data["start"], time_diff)
        stop = timestamp_to_real_time(data["start"], time_diff)
        is_file = data["is_file"]

        with PrivateInfluxDB(
            settings.INFLUX_URL,
            settings.INFLUX_AUTH_TOKEN,
            settings.INFLUX_ORG,
            settings.INFLUX_BUCKET) as pv_query:
            box_messages = pv_query.select(box_id=box_id, start=start, stop=stop, is_file=is_file)
        
        output_serializer = PrivateBoxMessagesSerialzier(data=box_messages, many=True)
        output_serializer.is_valid(raise_exception=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class EditPrivateMessage(APIView):
    def put(self, request, box_id:str):
        serializer = EditPrivateMessageInputSerializer(data=request.query_params.dict())
        serializer.is_valid()
        data = serializer.validated_data
        sender = request.user
        try:
            box = PrivateBox.objects.get(pk=box_id)
            if not(box.first_user != sender or box.second_user != sender):
                return Response(error.BAD_REQUEST, status=status.HTTP_406_NOT_ACCEPTABLE)
        except:
            return Response(error.OBJECT_NOT_FOUND, status=status.HTTP_400_BAD_REQUEST)
        
        log_id = data["log_id"]
        is_delete = data["is_delete"]
        start = timestamp_to_real_time(data["start"])
        stop = timestamp_to_real_time(data["stop"])

        with PrivateInfluxDB(
            settings.INFLUX_URL,
            settings.INFLUX_AUTH_TOKEN,
            settings.INFLUX_ORG,
            settings.INFLUX_BUCKET) as pv_query:
            message = pv_query.select(box_id=box_id, start=start, end=stop, id=log_id)
            if not message:
                return Response(error.OBJECT_NOT_FOUND, status=status.HTTP_400_BAD_REQUEST)
            if len(message) > 1:
                return Response(error.BAD_REQUEST, status.HTTP_300_MULTIPLE_CHOICES)
            message = message[0]
            # TODO: delete the log
            time = timestamp_to_real_time(message["datetime"])
            pv_query.insert(time=time, is_delete=is_delete, message=message["message"], file=message["file"])