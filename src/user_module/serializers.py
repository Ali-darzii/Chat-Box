from auth_module.models import User
from user_module.models import UserAvatar

from rest_framework import serializers


class UpdateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "phone_no")

class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAvatar
        exclude = ("user", "is_delete")


class GetUserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "phone_no", "avatars")

    avatars = serializers.SerializerMethodField()

    def get_avatars(self, obj):
        serializer =  AvatarSerializer(obj.avatars.filter(is_delete=False), many=True)
        return serializer.data
