from django.urls import path
from private_module.api import private

urlpatterns = [
    path("list/", private.ListPrivateBox.as_view(), name="list_private"),
    path("<int:box_id>/send-message/", private.SendPrivateMessage.as_view(), name="send_pv_message"),
    path("<int:box_id>/messages/", private.GetPrivateMessages.as_view(), name="get_pv_messages"),
]
