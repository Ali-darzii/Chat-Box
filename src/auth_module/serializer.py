import re
from rest_framework import serializers

from auth_module.models import User


class OTPSendSerializer(serializers.Serializer):
    phone_no = serializers.CharField()

    def validate_phone_no(self, phone_no: str):
        if not re.match(r'^09\d{9}$', phone_no):
            raise serializers.ValidationError('Phone number bad format.')
        return phone_no


class OTPCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone_no', "first_name", "last_name", "username"]
        extra_kwargs = {"password": {"write_only": True}}

    password = serializers.CharField(max_length=128, write_only=True, required=False)
    tk = serializers.CharField(min_length=6, max_length=6)

    def validate_phone_no(self, phone_no: str):
        if not re.match(r'^09\d{9}$', phone_no):
            raise serializers.ValidationError('Phone number bad format.')
        return phone_no

    def validate_tk(self, tk: str):
        if not tk.isnumeric():
            raise serializers.ValidationError("Char field is not numeric.")
        return tk