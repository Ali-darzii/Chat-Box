from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from group_module.models import GroupBox, GroupBoxAvatar
from group_module.serializers import (
    CreateGroupBoxSerializer,
    DetailGroupBoxSerializer,
    EditGroubBoxUsersSerializer,
    EditGroupBoxAdminsSerializer,
    EditGroupBoxNameSerializer,
    GroupBoxAvatarViewSetSerializer,
)


class CreateGroupBox(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CreateGroupBoxSerializer


class DetailGroupBox(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = DetailGroupBoxSerializer

    def get_queryset(self):
        return GroupBox.objects.filter(users=self.request.user)


class EditGroupBoxName(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EditGroupBoxNameSerializer

    def get_queryset(self):
        return GroupBox.objects.filter(admins=self.request.user)


class EditGroupBoxAdmins(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EditGroupBoxAdminsSerializer

    def get_queryset(self):
        return GroupBox.objects.filter(admins=self.request.user)


class EditGroupBoxUsers(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EditGroubBoxUsersSerializer

    def get_queryset(self):
        return GroupBox.objects.filter(admins=self.request.user)


class GroupBoxAvatarViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = GroupBoxAvatarViewSetSerializer

    def get_queryset(self):
        return GroupBoxAvatar.objects.filter(group__admins=self.request.user)
