from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView, ListAPIView
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from utils.response import ErrorResponses as error
from private_module.serializers import CreatePrivateBoxSerializer, ListPrivateBoxSerializer, SendPrivateMessageSerialzier
from private_module.models import PrivateBox
from private_module.influx.insert import PrivateInfluxDB



class ListPrivateBox(ListAPIView):
    """
    - List of users are in the same Box but authenticated user is excluded.
    """
    
    permission_classes = (IsAuthenticated,)
    serializer_class = ListPrivateBoxSerializer

    def get_queryset(self):
        return PrivateBox.objects.filter(
            Q(first_user=self.request.user) |Q(second_user=self.request.user)
        )
    

class CreatePrivatBox(CreateAPIView):
    """ 
    - We will use this if it's first message.
    - Then we call SendPrivateMessage EndPoint.
    - Same authenticad user can't make room with him self
    """
    
    permission_classes = (IsAuthenticated,)
    serializer_class = CreatePrivateBoxSerializer
    
    def perform_create(self, serializer):
        first_user = self.request.user
        second_user_id = serializer.validated_data["second_user"]
        if first_user.id == second_user_id:
            return Response(error.BAD_REQUEST, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(first_user=self.request.user)
    


class SendPrivateMessage(APIView):
    """
    With sending box_id you send message and file.
    Authenticated user must be in that box.
    """

    def post(self, request, box_id):
        serializer = SendPrivateMessageSerialzier(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        sender = request.user
        message = data.get("message", "")
        file = data.get("file", "")
        
        try:
            box = PrivateBox.objects.get(pk=box_id)
        except:
            return Response(error.OBJECT_NOT_FOUND, status=status.HTTP_400_BAD_REQUEST)

        if not(box.first_user != sender or box.second_user != sender):
            return Response(error.BAD_REQUEST, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        if file:
            file_name = default_storage.save(f"pv_files/{file.name}", ContentFile(file.read()))
            file_url = default_storage.url(file_name)

        with PrivateInfluxDB(
            settings.INFLUX_URL,
            settings.INFLUX_AUTH_TOKEN,
            settings.INFLUX_ORG,
            settings.INFLUX_BUCKET) as pv_query:
            pv_query.insert(box_id, sender.id, message, file_url)
            
        return Response({})