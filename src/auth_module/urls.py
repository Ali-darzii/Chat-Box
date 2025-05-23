from django.urls import path
from auth_module import views
urlpatterns = [
    path("otp/", views.OTPView.as_view(), name="otp"),
    path("token/", views.CustomTokenPairView.as_view(), name="token"),
    path("token/refresh/", views.CustomRefreshTokenView.as_view(), name="token_refresh"),
    path("token/verify/", views.CustomTokenVerify.as_view(), name="token_verify"),

]