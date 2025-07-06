from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    DestroyModelMixin
)

from django_filters.rest_framework import DjangoFilterBackend

from group_module.helper.filter import GroupBoxAvatarFilter
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


class GroupBoxAvatarViewSet(
    GenericViewSet, CreateModelMixin, ListModelMixin, DestroyModelMixin
):
    permission_classes = (IsAuthenticated,)
    serializer_class = GroupBoxAvatarViewSetSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = GroupBoxAvatarFilter

    def get_queryset(self):
        if self.request.method == "GET":
            return GroupBoxAvatar.objects.filter(group__users=self.request.user)
        return GroupBoxAvatar.objects.filter(group__admins=self.request.user)
