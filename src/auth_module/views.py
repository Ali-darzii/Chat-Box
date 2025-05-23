from http.client import responses

from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache as redis
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from auth_module.models import User
from auth_module.tasks import send_sms
from utils.response import ErrorResponses as error
from auth_module.serializer import OTPSendSerializer, OTPCheckSerializer
from utils.utils import generate_tk

class OTPView(APIView):
    def post(self, request):
        serializer = OTPSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_no = serializer.validated_data["phone_no"]

        current_tk = redis.get(f"otp_{phone_no}")
        if current_tk:
            return Response(error.TOKEN_IS_EXPIRED_OR_INVALID, tatus=status.HTTP_429_TOO_MANY_REQUESTS)
        tk = str(generate_tk())
        redis.set(f"otp_{phone_no}", tk, timeout=settings.OTP_TIMEOUT_DURATION)

        user, created = User.objects.get_or_create(phone_no=phone_no, defaults={"is_active": False})
        # send_sms.delay(phone_no, tk)

        return Response({"data":"Sms sent successfully", "new_user": created}, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = OTPCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        tk = data.pop("tk")
        password = data.pop("password")
        phone_no = serializer.validated_data["phone_no"]

        db_tk = redis.get(f"otp_{phone_no}")
        if not db_tk or db_tk != tk:
            return Response(error.CODE_IS_EXPIRED_OR_INVALID, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(phone_no=phone_no)
        except User.DoesNotExist:
            user = User(**data)
            user.set_password(password)
            user.last_login = timezone.now()
            user.save()

        refresh_token = str(RefreshToken.for_user(user))
        jwt = {
            "access_token": str(AccessToken.for_user(user)),
            "refresh_token": refresh_token,
            "user_id": user.id,
        }
        response = Response(jwt, status=status.HTTP_200_OK)
        response.set_cookie("refresh_token", refresh_token, httponly=True, secure=request.is_secure())

        return response



