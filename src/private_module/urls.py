from django.urls import path
from private_module import views

urlpatterns = [
    path("send-message/", views.SendPrivateMessageView.as_view(), name="send-private-message"),
]
