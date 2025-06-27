from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import UpdateAPIView, RetrieveAPIView

from auth_module.models import User
from user_module.serializers import UpdateUserSerializer, GetUserDetailSerializer


class EditeUser(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UpdateUserSerializer

    def get_object(self):
        return self.request.user

class GetUserDetail(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = GetUserDetailSerializer
    queryset = User.objects.all()



