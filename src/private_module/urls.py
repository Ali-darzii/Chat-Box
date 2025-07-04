from django.urls import path
from private_module.api import private

urlpatterns = [
    path("list/", private.ListPrivateBox.as_view(), name="list_private"),
    path("message/send/", private.SendPrivateMessage.as_view(), name="send_pv_message"),
    path("<int:box_id>/message/list/", private.ListPrivateMessages.as_view(), name="get_pv_messages"),
    path("<int:pk>/message/edit/", private.EditPrivateMessage.as_view(), name="update_pv_messages"),
    path("<int:message_id>/message/is-read/", private.PrivateMessageIsRead.as_view(), name="is_read_pv_messages"),

]