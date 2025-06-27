from django.core.exceptions import PermissionDenied
from rest_framework import serializers
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.exceptions import NotFound
from django.utils import timezone
from django.db import IntegrityError as UniqueError

from utils.response import ErrorResponses as error
from private_module.models import PrivateBox, PrivateMessage
from auth_module.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id","phone_no", "first_name", "avatar")


class ListPrivateBoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateBox
        fields = ("id", "user")

    user = serializers.SerializerMethodField()

    def get_user(self, instance):
        auth_user = self.context["request"].user
        front_user = instance.first_user if instance.second_user == auth_user else instance.second_user
        serializer = UserSerializer(front_user)
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

    def create(self, validated_data):
        sender = self.context["request"].user
        message = validated_data.pop("message", "")
        file_url = validated_data.pop("file", "")
        box_id = validated_data.pop("box_id")
        receiver_id = validated_data.pop("second_user_id")
        try:
            if box_id:
                box = PrivateBox.objects.get(pk=box_id)
            else:
                # rare case
                box = PrivateBox.objects.create(first_user=sender, second_user_id=receiver_id)
        except PrivateBox.DoesNotExist:
            raise NotFound
        except UniqueError:
            raise serializers.ValidationError(error.BAD_REQUEST)

        if not (box.first_user != sender or box.second_user != sender):
            raise PermissionDenied

        box.last_message = timezone.now()
        box.save()
        return PrivateMessage.objects.create(message=message, file=file_url, sender=sender, box=box)


class UserPrivateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "phone_no", "first_name", "avatar")


class PrivateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateMessage
        exclude = ("updated_at",)

    box = serializers.IntegerField(source="box.id")
    sender = UserPrivateMessageSerializer()


class EditPrivateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateMessage
        fields = ("id", "message", "is_delete")

    id = serializers.IntegerField(read_only=True)
    is_delete = serializers.BooleanField(required=False)

    def validate_is_delete(self, is_delete):
        if is_delete:
            raise serializers.ValidationError(error.BAD_FORMAT)
        return is_delete
