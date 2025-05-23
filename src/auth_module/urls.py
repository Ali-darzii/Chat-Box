from django.urls import path
from auth_module import views
urlpatterns = [
    path("otp/", views.OTPView.as_view(), name="otp"),
]