from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from group_module.models import GroupBox
from group_module.serializers import CreateGroupBoxSerializer, GroupBoxDetailSerializer


class CreateGroupBox(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CreateGroupBoxSerializer

class GroupBoxDetail(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = GroupBoxDetailSerializer

    def get_queryset(self):
        return GroupBox.objects.filter(users=self.request.user)