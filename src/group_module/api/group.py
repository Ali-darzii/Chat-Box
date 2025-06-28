from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from group_module.serializers import CreateGroupBoxSerializer


class CreateGroupBox(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CreateGroupBoxSerializer