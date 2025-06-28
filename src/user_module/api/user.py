from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import UpdateAPIView, RetrieveAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from auth_module.models import User
from user_module.serializers import UpdateUserSerializer, GetUserDetailSerializer, AddAvatarSerializer, \
    GetUserListSerializer




class PublicGetUserDetail(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = GetUserDetailSerializer
    queryset = User.objects.all()


class PublicGetUserList(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = GetUserListSerializer
    queryset = User.objects.all()



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
    