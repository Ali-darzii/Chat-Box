from rest_framework import serializers
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
    
    

class SendPrivateMessageSerialzier(serializers.Serializer):
    message = serializers.CharField(required=False)
    file = serializers.FileField(required=False, max_length=100)
    
    def validate(self, attrs):
        file = attrs.get("file")
        message = attrs.get("message")
        if not(message or file):
            raise serializers.ValidationError(error.BAD_REQUEST)
        
        return attrs
    
    def file_validate(self, file):
        if file:
            print(file.size)
        return file