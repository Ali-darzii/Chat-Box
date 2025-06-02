from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView, GenericAPIView
from select import select

from auth_module.models import User
from private_module.models import PrivateBox
from private_module.serializers import SendPrivateMessageSerializer, GetUsersByBoxSerializer


class GetPrivateBoxView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = GetUsersByBoxSerializer

    def get(self, request):
        users = User.objects.all().select_related("private_box_id")



class CreatePrivateMessageView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SendPrivateMessageSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request)


