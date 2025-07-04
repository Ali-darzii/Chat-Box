from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from group_module.models import GroupBox
from group_module.serializers import (
    CreateGroupBoxSerializer,
    DetailGroupBoxSerializer,
    EditGroupBoxSerializer,
)


class CreateGroupBox(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CreateGroupBoxSerializer


class DetailGroupBox(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = DetailGroupBoxSerializer

    def get_queryset(self):
        return GroupBox.objects.filter(users=self.request.user)


class EditGroupBox(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EditGroupBoxSerializer
    
    def get_queryset(self):
        return GroupBox.objects.filter(admins=self.request.user)