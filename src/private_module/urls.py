from django.urls import path
from private_module.api import private

urlpatterns = [
    path("list/", private.ListPrivateBox.as_view(), name="list_private"),
    path("create/", private.CreatePrivateBox.as_view(), name="create_private"),
    path("<int:box_id>/send-message/", private.SendPrivateMessage.as_view(), name="send_pv_message"),
]
