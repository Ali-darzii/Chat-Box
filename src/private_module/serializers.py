from django.core.exceptions import PermissionDenied
from rest_framework import serializers
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.exceptions import NotFound
from django.utils import timezone
from django.db import IntegrityError as UniqueError

from user_module.serializers import AvatarSerializer
from utils.response import ErrorResponses as error
from private_module.models import PrivateBox, PrivateMessage
from auth_module.models import User


class PrivateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "phone_no", "avatar")

    avatar = serializers.SerializerMethodField()

    def get_avatar(self, obj):
        serializer =  AvatarSerializer(obj.avatars.filter(is_delete=False).order_by("-created_at").last())
        return serializer.data


class ListPrivateBoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateBox
        fields = ("id", "user")

    user = serializers.SerializerMethodField()

    def get_user(self, instance):
        auth_user = self.context["request"].user
        front_user = instance.first_user if instance.second_user == auth_user else instance.second_user
        serializer = PrivateUserSerializer(front_user)
        return serializer.data


class SendPrivateMessageSerializer(serializers.Serializer):
    box_id = serializers.IntegerField(default=0, min_value=1)
    receiver_id = serializers.IntegerField(min_value=1)
    message = serializers.CharField(required=False)
    file = serializers.FileField(required=False, max_length=100)

    def validate(self, attrs):
        file = attrs.get("file")
        message = attrs.get("message")
        if not (message or file):
            raise serializers.ValidationError(error.MISSING_PARAMS)

        return attrs

    def validate_file(self, file):
        if file:
            if file.size > 10 * 1024 * 1024:
                raise serializers.ValidationError("File must contain less than 10Mb volume.")

            file_name = default_storage.save(f"pv_files/{file.name}", ContentFile(file.read()))
            file_url = default_storage.url(file_name)
            return file_url

        return file


class PrivateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateMessage
        exclude = ("updated_at",)

    box = serializers.IntegerField(source="box.id")
    sender = PrivateUserSerializer()


class EditPrivateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateMessage
        fields = ("id", "message", "is_delete")

    is_delete = serializers.BooleanField(required=False)

    def validate_is_delete(self, is_delete):
        if is_delete:
            raise serializers.ValidationError(error.BAD_FORMAT)
        return is_delete
