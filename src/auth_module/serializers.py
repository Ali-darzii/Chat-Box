import re
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from utils.response import ErrorResponses as error
from auth_module.models import User



class OTPSendSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone_no', "password","first_name", "last_name", "username"]

    phone_no = serializers.CharField()
    password = serializers.CharField(max_length=128, required=False)

    def validate_phone_no(self, phone_no: str):
        if not re.match(r'^09\d{9}$', phone_no):
            raise serializers.ValidationError(error.BAD_FORMAT)
        return phone_no

    def validate_password(self, password: str):
        if not re.fullmatch(r"^(?=.*[A-Z])(?=.*\d).+$", password):
            raise serializers.ValidationError(error.BAD_FORMAT)
        return password

    def validate_username(self, username: str):
        if not re.fullmatch(r"^[a-zA-Z][a-zA-Z0-9_]{2,23}[a-zA-Z0-9]$", username):
            raise serializers.ValidationError(error.BAD_FORMAT)
        return username



class OTPCheckSerializer(serializers.Serializer):
    phone_no = serializers.CharField()
    tk = serializers.CharField(min_length=6, max_length=6)

    def validate_phone_no(self, phone_no: str):
        if not re.match(r'^09\d{9}$', phone_no):
            raise serializers.ValidationError(error.BAD_FORMAT)
        return phone_no

    def validate_tk(self, tk: str):
        if not tk.isnumeric():
            raise serializers.ValidationError(error.BAD_FORMAT)
        return tk



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['phone_no'] = user.phone_no
        return token


class OTPResetPasswordSerializer(OTPCheckSerializer):
    password = serializers.CharField(max_length=128)