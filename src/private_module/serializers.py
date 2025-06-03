from rest_framework import serializers
from django.db import IntegrityError as UniqueError
from utils.response import ErrorResponses as error
from private_module.models import PrivateBox



class CreatePrivateBoxSerializer(serializers.ModelSerializer):
    class Meta:
            model = PrivateBox
            fields = "__all__"
        
    
    def validate(self, attrs:dict):
        if attrs["first_user"] == attrs["second_user"]:
            raise serializers.ValidationError(error.BAD_FORMAT)
        return attrs
    
    def post(self, request, *args, **kwargs):
        try: 
            return super().post(request, *args, **kwargs)
        except UniqueError:
            raise serializers.ValidationError(error.BAD_FORMAT)