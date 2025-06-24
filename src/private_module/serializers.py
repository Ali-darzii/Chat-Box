from rest_framework import serializers
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db import IntegrityError as UniqueError

from utils.response import ErrorResponses as error
from private_module.models import PrivateBox
from auth_module.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("phone_no","first_name", "avatar")



class ListPrivateBoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateBox
        fields = ("id","user")
        
    user = serializers.SerializerMethodField()
    
    def get_user(self, instance):
        auth_user = self.context["request"].user
        print(instance)
        front_user =  instance.first_user if instance.second_user == auth_user else instance.second_user
        serializer = UserSerializer(front_user)
        return serializer.data
    
class CreatePrivateBoxSerializer(serializers.ModelSerializer):
    
    class Meta:
            model = PrivateBox
            exclude = ("first_user",)

    def create(self, validated_data):
        user = self.context["request"].user
        second_user = validated_data["second_user"]
        if user.id == second_user.id:
            raise serializers.ValidationError(error.BAD_REQUEST)
        try:
            return super().create(validated_data)
        except UniqueError:
            raise serializers.ValidationError(error.BAD_REQUEST)



class SendPrivateMessageSerializer(serializers.Serializer):
    message = serializers.CharField(required=False)
    file = serializers.FileField(required=False, max_length=100)
    
    def validate(self, attrs):
        file = attrs.get("file")
        message = attrs.get("message")
        if not(message or file):
            raise serializers.ValidationError(error.MISSING_PARAMS)
        
        return attrs

    def validate_file(self, file):
        if file:
            if file.size > 10 * 1024 * 1024:
                raise serializers.ValidationError("File must contain less than 10Mb volume.")

            file_name = default_storage.save(f"pv_files/{file.name}", ContentFile(file.read()))
            file_url = default_storage.url(file_name)
            print(file_url)
            return file_url

        return file


class GetPrivateMessagesInputSerialzier(serializers.Serializer):
    start = serializers.IntegerField(min_value=0)
    stop = serializers.IntegerField(min_value=10)
    is_file = serializers.BooleanField(default=False, required=False)


class PrivateBoxMessagesSerialzier(serializers.Serializer):
    id = serializers.CharField()
    datetime = serializers.IntegerField()
    message = serializers.CharField()
    file = serializers.CharField()


class EditPrivateMessageInputSerializer(serializers.Serializer):
    log_id = serializers.CharField()
    start = serializers.IntegerField()
    stop = serializers.IntegerField()
    is_delete = serializers.BooleanField(default=False, required=False)