from rest_framework import serializers
from django.db import IntegrityError as UniqueError
from utils.response import ErrorResponses as error
from private_module.models import PrivateBox


class GetPrivateBoxSerializer(serializers.Serializer):
    class Meta:
        model = PrivateBox
        fields = ("id","user")
        
    user = serializers.SerializerMethodField()
    
    def get_user(self, obj: PrivateBox):
        auth_user = self.context["request"].user
        return obj.first_user if obj.second_user == auth_user else obj.second_user


class PrivateBoxSerializer(serializers.ModelSerializer):

    
    class Meta:
            model = PrivateBox
            fields = "__all__"
        
    
    def validate(self, attrs:dict):
        if attrs["first_user"] == attrs["second_user"]:
            raise serializers.ValidationError(error.BAD_FORMAT)
        return attrs
    
    
