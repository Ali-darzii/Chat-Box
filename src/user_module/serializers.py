from auth_module.models import User
from rest_framework import serializers


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "avatar")
