from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache as redis
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
import logging

from auth_module.models import User
from auth_module.tasks import send_sms
from utils.response import ErrorResponses as error
from auth_module.serializer import OTPSendSerializer, OTPCheckSerializer, CustomTokenObtainPairSerializer
from utils.throttle import SendOTPThrottle, CheckOTPThrottle, UserExistThrottle
from utils.utils import generate_tk

logger = logging.getLogger("django")

class OTPView(APIView):
    """
    Logic:
        -get
            After client put his phone_no we check user registered or not.
        -post
            In general this request send OTP.
            Front from previous get request will notice if user was registered
            will sent post request directly and if not, will get the user info
            then sent a post request
        -put
            will check the OTP.


    """

    def get(self, request):
        """ User Exist? """
        serializer = OTPSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_no = serializer.validated_data['phone_no']
        data = {"data":"success"}
        try:
            User.objects.get(phone_no=phone_no)
            data["user_exist"] = True
            return Response(data=data,status=status.HTTP_200_OK)
        except User.DoesNotExist:
            data["user_exist"] = False
            return Response(data=data,status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """ Send OTP """
        serializer = OTPSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        phone_no = data["phone_no"]

        prev_tk = redis.get(f"otp_{phone_no}")
        if prev_tk:
            return Response(error.TOKEN_IS_EXPIRED_OR_INVALID, status=status.HTTP_429_TOO_MANY_REQUESTS)
        tk = generate_tk()
        redis.set(f"otp_{phone_no}", tk, timeout=settings.OTP_TIMEOUT_DURATION)

        user_exist = User.objects.filter(phone_no=phone_no).exists()
        if user_exist:
            return Response({"data": "Sms sent successfully", "new_user": False}, status=status.HTTP_200_OK)
        username_exist = User.objects.filter(username=phone_no).exists()
        if username_exist:
            return Response(error.field_is_unique("username"), status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User(
                phone_no=phone_no,
                username=data["username"],
                first_name=data["first_name"],
                last_name=data["last_name"],
            )
            user.set_password(data["password"])
            user.save()
        except KeyError:
            return Response(error.MISSING_PARAMS, status=status.HTTP_400_BAD_REQUEST)
        send_sms.delay(phone_no, tk)
        return Response({"data":"Sms sent successfully", "new_user": True}, status=status.HTTP_200_OK)

    def put(self, request):
        """ Check OTP """
        serializer = OTPCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_no = serializer.validated_data["phone_no"]
        tk = serializer.validated_data["tk"]

        db_tk = redis.get(f"otp_{phone_no}")
        if not db_tk or db_tk != tk:
            return Response(error.CODE_IS_EXPIRED_OR_INVALID, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(phone_no=phone_no)
            user.last_login = timezone.now()
            user.save()
        except User.DoesNotExist:
            return Response(error.TOKEN_IS_EXPIRED_OR_INVALID, status=status.HTTP_400_BAD_REQUEST)

        refresh_token = str(RefreshToken.for_user(user))
        jwt = {
            "access": str(AccessToken.for_user(user)),
            "refresh": refresh_token,
            "user_id": user.id,
        }
        response = Response(jwt, status=status.HTTP_200_OK)
        response.set_cookie("refresh", refresh_token, httponly=True, secure=request.is_secure())

        return response


    def get_throttles(self):
        method = self.request.method
        if method == "POST":
            return [SendOTPThrottle()]
        elif method == "PUT":
            return [CheckOTPThrottle()]

        return [UserExistThrottle()]

class CustomTokenPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            logger.info(response.data)
            refresh_token = response.data["refresh"]
            if not refresh_token:
                raise
            response.set_cookie(
                "refresh",
                refresh_token,
                httponly=True,
                secure=request.is_secure(),
            )
            return response
        except Exception as e:
            logger.critical(e, exc_info=True)
            return Response(error.SOMETHING_WENT_WRONG, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenVerify(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        resp = Response({"valid": True})
        return resp


class CustomRefreshTokenView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            request.data["refresh"] = request.COOKIES.get("refresh")
            response = super().post(request, *args, **kwargs)
            response.set_cookie(
                "refresh",
                response.data["refresh"],
                httponly=True,
                secure=request.is_secure(),
            )
            return response
        except Exception as e:
            logger.critical(f"Refresh Token API, {e}", exc_info=True)
            return Response(error.SOMETHING_WENT_WRONG, status=status.HTTP_400_BAD_REQUEST)
