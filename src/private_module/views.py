from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView

from private_module.serializer import PrivateMessageSerializer


class SendPrivateMessageView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PrivateMessageSerializer

    def post(self, request, *args, **kwargs):
        response = super(SendPrivateMessageView, self).post(request, *args, **kwargs)
        # TODO: influxdb
        return response

