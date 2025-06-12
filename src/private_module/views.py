from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView, ListAPIView
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.conf import settings

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
        second_user_id = serializer.data["second_user"]
        if first_user.id == second_user_id:
            return Response(error.BAD_REQUEST, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(first_user=self.request.user)
    


class SendPrivateMessage(APIView):
    

    def post(self, request, box_id):
        serializer = SendPrivateMessageSerialzier(data=request.data, files=request.FILES)
        serializer.is_valid(raise_exception=True)
        print(serializer.data)
        return Response({},status=status.HTTP_200_OK)
        message = serializer.get("message", "")
        file = serializer.get("file", "")
        if file:
            pass
        
        with PrivateInfluxDB(
            settings.INFLUX_URL,
            settings.INFLUX_AUTH_TOKEN,
            settings.INFLUX_ORG,
            settings.INFLUX_BUCKET) as pv_query:
            pv_query.insert(box_id=box_id)
            
            