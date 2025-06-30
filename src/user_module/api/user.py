from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import UpdateAPIView, RetrieveAPIView, ListAPIView
from rest_framework.viewsets import ModelViewSet
from django.db.models import Q
from auth_module.models import User
from private_module.models import PrivateBox
from user_module.serializers import UpdateUserSerializer, GetUserDetailSerializer, AddAvatarSerializer

"""
Public API's have all user access.
Private API's have only authenticated user access.
"""


class PublicUserDetail(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = GetUserDetailSerializer

    def get_queryset(self):
        user = self.request.user
        return PrivateBox.objects.filter(
            Q(first_user=user)| Q(second_user=user)
        ).select_related("first_user", "second_user").order_by("-id")

class PrivateEditUser(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UpdateUserSerializer

    def get_object(self):
        return self.request.user

class PrivateAvatarViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = AddAvatarSerializer

    def get_queryset(self):
        return self.request.user.avatars.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
