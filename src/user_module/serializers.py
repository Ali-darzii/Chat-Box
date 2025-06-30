from django.utils.functional import cached_property

from auth_module.models import User
from private_module.models import PrivateBox
from user_module.models import UserAvatar

from rest_framework import serializers
from utils.response import ErrorResponses as error


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username")


class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAvatar
        exclude = ("user", "is_delete")


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "phone_no", "avatars")

    avatars = serializers.SerializerMethodField()

    def get_avatars(self, obj):
        serializer = AvatarSerializer(obj.avatars.filter(is_delete=False), many=True)
        return serializer.data


class GetUserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateBox
        fields = ("id", "user")

    user = serializers.SerializerMethodField()

    def get_user(self, instance):
        auth_user = self.context["request"].user
        front_user = instance.first_user if instance.second_user == auth_user else instance.second_user
        serializer = UserDetailSerializer(front_user)
        return serializer.data


class AddAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAvatar
        fields = "__all__"
        extra_kwargs = {
            "avatar": {"required": True},
            "user": {"read_only": True},
            "created_at": {"read_only": True},
        }

    def create(self, validated_data):
        validated_data.pop("is_delete", None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        is_delete = validated_data.get("is_delete")
        if is_delete is None:
            raise serializers.ValidationError(error.BAD_FORMAT)
        data = {"is_delete": is_delete}
        return super().update(instance, data)
