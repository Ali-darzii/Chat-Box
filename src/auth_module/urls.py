from django.urls import path
from auth_module.api import auth
urlpatterns = [
    path("otp/", auth.OTPView.as_view(), name="otp"),
    path("token/", auth.CustomTokenPairView.as_view(), name="token"),
    path("token/refresh/", auth.CustomRefreshTokenView.as_view(), name="token_refresh"),
    path("token/verify/", auth.CustomTokenVerify.as_view(), name="token_verify"),
    path("logout/", auth.Logout.as_view(), name="logout"),
    path("otp/reset/password/", auth.OTPResetPassword.as_view(), name="otp_reset_password"),

]