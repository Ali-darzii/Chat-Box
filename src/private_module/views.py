from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView, GenericAPIView

from private_module.serializers import CreatePrivateBoxSerializer


class CreatePrivatBox(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CreatePrivateBoxSerializer
    



