from django.urls import path
from private_module import views

urlpatterns = [
    path("list/", views.ListPrivateBox.as_view(), name="list_private"),
    path("create/", views.CreatePrivatBox.as_view(), name="create_private"),
    path("send-message/<int:box_id>/", views.SendPrivateMessage.as_view(), name="send_pv_message"),
]
